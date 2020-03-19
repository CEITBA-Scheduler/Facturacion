import datetime
import logging
import os
from datetime import date

from constance import config
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import DateField, ExpressionWrapper, F, Max, Sum
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from facturacion.models import Student, Enrollment, Report, Purchase, PurchaseItem, Product, Service

logger = logging.getLogger(__name__)

if not settings.DEBUG:
    from datadog import statsd


class AnnotatedSportCertificateModelManager(models.Manager):
    def get_queryset(self):
        return super(AnnotatedSportCertificateModelManager, self).get_queryset().annotate(
            expiration_date=ExpressionWrapper(
                F('date_emitted') + datetime.timedelta(days=365), output_field=DateField()
            )
        )


class JournalEntry(models.Model):
    who = models.CharField(
        verbose_name='responsable',
        max_length=100,
    )
    description = models.TextField(
        verbose_name=_("description"),
        max_length=500,
    )
    amount_in = models.DecimalField(
        verbose_name='ingresos',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    amount_out = models.DecimalField(
        verbose_name='egresos',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    date_created = models.DateField(
        verbose_name='fecha de egreso',
        default=None,
        null=True,
        blank=True,
    )
    date_paid = models.DateField(
        verbose_name=_('date paid'),
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Entrada de Libro Diario'
        verbose_name_plural = 'Entradas de Libro Diario'
        permissions = (
            ('save_journalentry', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return "%d %s" % (self.id, self.description)


class PrinterCount(models.Model):
    member = models.OneToOneField(
        to=Student,
        verbose_name=_('member'),
    )
    print_count = models.PositiveSmallIntegerField(
        verbose_name='impresiones',
        default=0
    )
    last_updated = models.DateTimeField(
        verbose_name='Ultima actualizacion',
        default=timezone.now,
        db_index=True
    )

    class Meta:
        verbose_name = 'Cuenta de Impresión'
        verbose_name_plural = 'Cuentas de Impresión'
        permissions = (
            ('save_printercount', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return 'Cuenta de Impresiones de %s' % self.member.name


class PrinterReport(models.Model):
    date_uploaded = models.DateTimeField(
        verbose_name=_('date uploaded'),
        default=timezone.now,
        db_index=True
    )
    file = models.FileField(
        verbose_name=_('report file'),
        upload_to='printer_reports/',
    )

    class Meta:
        verbose_name = 'Reporte de impresión'
        verbose_name_plural = 'Reportes de impresión'
        get_latest_by = "date_uploaded"
        permissions = (
            ('save_printerreport', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return 'Reporte de impresion al %s' % self.date_uploaded

    def save(self, *args, **kwargs):
        self.file.name = 'Reporte de impresion al %s.csv' % date.today()

        super(PrinterReport, self).save(*args, **kwargs)

        from_datetime = PrinterCount.objects.aggregate(Max('last_updated'))['last_updated__max']
        # from_datetime = timezone.make_naive(from_datetime)

        print_product = Product.active.get(name=config.IMPRESIONES_PRODUCT)

        logger.info("Processing printings from date %s", from_datetime)

        _ = self.file.readline()  # brand
        _ = self.file.readline()  # header

        import csv

        # TODO: No mandar el mail mas de una vez

        while True:
            line = self.file.readline()
            line = line.strip()
            if not line:
                break

            parsed_line = csv.reader([line.decode("latin1")])
            data = list(parsed_line)[0]

            print_date = datetime.datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S")
            print_date = timezone.make_aware(print_date)

            if print_date < from_datetime:
                continue

            try:
                legajo = int(data[1])
                paginas = int(data[2])
            except:
                continue

            print_count = PrinterCount.objects.prefetch_related('member').get(member__student_id=legajo)
            print_count.print_count += paginas
            print_count.last_updated = print_date
            print_count.save()

            if print_count.print_count > config.IMPRESIONES_GRATIS and config.IMPRESIONES_SEND_EMAIL:
                member = print_count.member
                logger.info("Sending notification email for printing quota exceeded to %s", member)

                context = {
                    'full_name': member.name,
                    'free_prints': config.IMPRESIONES_GRATIS,
                    'page_price': print_product.price
                }
                subject = 'CEITBA: Te has excedido de las impresiones gratis!'

                html_content = render_to_string('informacion/emails/free_prints_exceeded.html', context)

                if member.email is not None and member.email:
                    to = [member.email]

                    msg = EmailMessage(
                        subject=subject,
                        body=html_content,
                        to=to,
                        reply_to=[config.CEITBA_EMAIL])
                    msg.content_subtype = "html"
                    try:
                        msg.send()
                    except Exception as e:
                        logger.exception("Failed to send email. to=%s", str(to))

        if not settings.DEBUG:
            total = PrinterCount.objects.aggregate(total=Sum('print_count'))['total']
            statsd.gauge('ceitba.impresiones.count', total)


def build_certificate_filename(instance, filename):
    return 'sport_certificates/%s_%s%s' % (instance.member.name, instance.date_emitted, os.path.splitext(filename)[1])


class SportCertificate(models.Model):
    member = models.ForeignKey(
        to=Student,
        verbose_name=_('member')
    )
    date_uploaded = models.DateField(
        verbose_name=_('date uploaded'),
        default=date.today,
        db_index=True
    )
    certificate = models.FileField(
        verbose_name=_('certificate'),
        upload_to=build_certificate_filename,
    )
    date_emitted = models.DateField(
        verbose_name='fecha de emisión',
    )

    class Meta:
        verbose_name = 'Certificado médico'
        verbose_name_plural = 'Certificados médicos'
        get_latest_by = "date_emitted"
        permissions = (
            ('save_sportcertificate', 'NEW: Can save changes made to the model'),
        )

    objects = AnnotatedSportCertificateModelManager()

    def is_valid(self):
        return (date.today() - self.date_emitted).days < 365

    def __str__(self):
        return 'Certificado de %s' % self.member


class InventoryCategory(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = 'Categoría de inventario'
        verbose_name_plural = 'Categoras de inventario'
        permissions = (
            ('save_inventorycategory', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return self.name


class InventoryLocation(models.Model):
    location = models.CharField(
        verbose_name='ubicación',
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = 'Ubicación de Inventario'
        verbose_name_plural = 'Ubicaciones de Inventario'
        permissions = (
            ('save_inventorylocation', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return self.location


class InventoryEntry(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
    )
    date_created = models.DateField(
        verbose_name='fecha de entrada',
        default=date.today,
    )
    description = models.TextField(
        verbose_name=_("description"),
        max_length=500,
    )
    location = models.ForeignKey(
        to=InventoryLocation,
        verbose_name='ubicación',
    )
    original_value = models.DecimalField(
        verbose_name='valor de adquisición',
        max_digits=8,
        decimal_places=2
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='cantidad'
    )
    categories = models.ManyToManyField(
        to=InventoryCategory,
        verbose_name='categorias'
    )
    acquired = models.BooleanField(
        verbose_name='adquirido',
        default=True
    )
    journal_entries = models.ManyToManyField(
        to=JournalEntry,
        verbose_name='entradas del libro diario'
    )
    product = models.ForeignKey(
        to=Product,
        verbose_name='producto',
        null=True,
        default=None,
        blank=True
    )

    class Meta:
        verbose_name = 'Entrada de inventario'
        verbose_name_plural = 'Entradas de inventario'
        permissions = (
            ('save_inventoryentry', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return '%d %s en %s' % (self.quantity, self.name, self.location)


class YMCAFamilyMember(models.Model):
    enrollment = models.OneToOneField(
        to=Enrollment,
        verbose_name=_('enrollment'),
        on_delete=models.CASCADE,
    )
    family_members = models.TextField(
        verbose_name='Familiares',
        help_text='Un familiar por linea.'
    )

    class Meta:
        verbose_name = 'Miembro familiar del YMCA'
        verbose_name_plural = 'Miembros familiares del YMCA'
        permissions = (
            ('save_ymcafamilymember', 'NEW: Can save changes made to the model'),
        )

    def save(self, *args, **kwargs):
        self.family_members = self.family_members.strip()
        super(YMCAFamilyMember, self).save(*args, **kwargs)


class PrintingException(models.Model):
    member = models.OneToOneField(
        to=Student,
        verbose_name=_('member'),
    )
    count = models.PositiveSmallIntegerField(
        verbose_name=_('count')
    )
    date = models.DateTimeField(
        verbose_name=_('date created'),
        default=timezone.now,
        db_index=True
    )

    class Meta:
        verbose_name = 'Excepcion de Impresion'
        verbose_name_plural = 'Excepciones de Impresiones'
        permissions = (
            ('save_printingexception', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return 'Excepcion de %d paginas para %s' % (self.count, self.member.name)


class AlquilerMate(models.Model):
    member = models.ForeignKey(
        to=Student,
        verbose_name=_('member')
    )
    time_taken = models.DateTimeField(
        verbose_name='Fecha alquiler',
        default=timezone.now,
        db_index=True
    )
    time_returned = models.DateTimeField(
        verbose_name='Fecha devolución',
        null=True,
        blank=True
    )
    kit_number = models.PositiveSmallIntegerField(
        verbose_name='Número de Kit'
    )
    amount_donated = models.PositiveSmallIntegerField(
        verbose_name='Monto donado',
        default=0,
        help_text='Dejar en 0 para cobro por cuota.'
    )
    paid_in_cash = models.BooleanField(
        verbose_name='Paga en Efectivo',
        help_text='Al desmarcarlo se le agregará una compra equivalente de forma automática.',
        default=True
    )

    def save(self, *args, **kwargs):
        super(AlquilerMate, self).save(*args, **kwargs)

        if not self.paid_in_cash:
            product = Product.objects.get(name=config.MATE_PRODUCT_NAME)

            purchase = Purchase(student=self.member)
            purchase.save()

            item = PurchaseItem(product=product, quantity=1, purchase=purchase)
            item.save()

    class Meta:
        verbose_name = 'Alquiler de Mate'
        verbose_name_plural = 'Alquileres de Mate'
        permissions = (
            ('save_alquilermate', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return 'Kit %s a %s' % (self.kit_number, self.member.name)


class MediaObject(models.Model):
    screen_time = models.PositiveSmallIntegerField(
        verbose_name='tiempo en pantalla',
        help_text="En segundos"
    )
    media_file = models.FileField(
        verbose_name='archivo multimedia',
        upload_to='office_media',
    )
    published_tv = models.BooleanField(
        verbose_name='publicado en tv',
        default=True,
        db_index=True
    )
    published_web = models.BooleanField(
        verbose_name='publicado en web',
        default=True,
        db_index=True
    )
    published_apuntes = models.BooleanField(
        verbose_name='publicado en apuntes',
        default=True,
        db_index=True
    )

    def __str__(self):
        return "%s" % self.media_file.name

    class Meta:
        verbose_name = 'Archivo Multimedia'
        verbose_name_plural = 'Archivos Multimedia'
        permissions = (
            ('save_mediaobject', 'NEW: Can save changes made to the model'),
        )

    def delete(self, *args, **kwargs):
        super(MediaObject, self).delete(*args, **kwargs)


class Lend(models.Model):
    member = models.ForeignKey(
        to=Student,
        verbose_name='miembro'
    )
    lended_object = models.TextField(
        verbose_name='objeto prestado'
    )
    time_taken = models.DateTimeField(
        verbose_name='Fecha de prestamo',
        default=timezone.now,
        db_index=True
    )
    time_returned = models.DateTimeField(
        verbose_name='fecha de devolución',
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        verbose_name = 'Prestamo'
        verbose_name_plural = 'Prestamos'
        permissions = (
            ('save_lend', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return "%s a %s" % (self.lended_object, self.member)


class Document(models.Model):
    title = models.CharField(
        verbose_name='titulo',
        max_length=300
    )
    document = models.FileField(
        verbose_name='documento',
        upload_to='documents',
    )

    def __str__(self):
        return "%s" % self.title

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        permissions = (
            ('save_document', 'NEW: Can save changes made to the model'),
        )

    def delete(self, *args, **kwargs):
        self.document.delete()
        super(Document, self).delete(*args, **kwargs)


class Reminder(models.Model):
    content = models.TextField(
        verbose_name='contenido'
    )
    completed = models.BooleanField(
        verbose_name='completado',
        help_text='Marquelo para marcar el recordatorio como completado'
    )

    class Meta:
        verbose_name = 'Recordatorio'
        verbose_name_plural = 'Recordatorios'
        permissions = (
            ('save_reminder', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return str(self.id)


class RangedExport(models.Model):
    service = models.ForeignKey(
        to=Service,
        verbose_name='servicio'
    )
    start_date = models.DateField(
        verbose_name='fecha inicio'
    )
    end_date = models.DateField(
        verbose_name='fecha fin'
    )
    exported_file = models.FileField(
        verbose_name='archivo exportado',
        upload_to='ranged_exports'
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            from facturacion.export import exportar_altas_y_bajas

            file_obj = exportar_altas_y_bajas(self.service.name,
                                              self.start_date,
                                              self.end_date)

            file_name = "Altas y bajas en %s del %s al %s.xlsx" % (self.service.name,
                                                                   self.start_date,
                                                                   self.end_date)
            file_obj.seek(0)

            self.exported_file.save(file_name, ContentFile(file_obj.getvalue()), save=False)

        super(RangedExport, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Exportar por Rango'
        verbose_name_plural = 'Exportar por Rango'
        permissions = (
            ('save_rangedexport', 'NEW: Can save changes made to the model'),
        )

    def clean(self):

        if self.end_date <= self.start_date:
            raise ValidationError('La fecha de comienzo debe ser menor a la de final', code='invalid')

    def __str__(self):
        return "Altas y bajas en %s del %s al %s.xlsx" % (self.service.name,
                                                          self.start_date,
                                                          self.end_date)

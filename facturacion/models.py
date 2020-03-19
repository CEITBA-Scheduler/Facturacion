import datetime
import logging
from datetime import date

from constance import config
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.validators import validate_email, MinValueValidator
from django.db import transaction, models
from django.db.models import Sum, DecimalField, OuterRef, Exists, F
from django.db.models.functions import Coalesce
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.dates import MONTHS

logger = logging.getLogger(__name__)


class ActiveModelManager(models.Manager):
    """
    Manager que solo devuelve los objetos que no fueron dados de baja en el queryset.
    """

    def get_queryset(self):
        return super(ActiveModelManager, self).get_queryset().filter(date_removed__isnull=True)


class ActiveStudentModelManager(models.Manager):
    """
    Manager que solo devuelve los alumnos que son socios activos del CEITBA
    """

    def get_queryset(self):
        return super(ActiveStudentModelManager, self).get_queryset().filter(
            enrollment__service__name__exact=config.CEITBA_SERVICE_NAME,
            enrollment__date_removed__isnull=True)


class AnnotatedStudentModelManager(models.Manager):
    """
    Manager que solo devuelve los alumnos que son socios activos del CEITBA
    """

    def get_queryset(self):
        queryset = super(AnnotatedStudentModelManager, self).get_queryset()

        is_active_query = Enrollment.objects.filter(
            service__name=config.CEITBA_SERVICE_NAME,
            date_removed__isnull=True,
            student__id=OuterRef('pk'),
        )

        return queryset.annotate(
            is_active=Exists(is_active_query)
        )


def validate_itba_email(email):
    message = _('You need to enter an ITBA email address.')

    validate_email(email)

    if config.ITBA_EMAIL_DOMAIN not in email:
        raise ValidationError(message, params={'value': email})


class Student(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=300,
    )
    student_id = models.PositiveIntegerField(
        verbose_name=_('id'),
        unique=True,
        db_index=True
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )
    date_removed = models.DateField(
        verbose_name=_('date removed'),
        null=True, blank=True,
        db_index=True
    )
    email = models.EmailField(
        verbose_name=_('email'),
        blank=True,
        validators=[validate_itba_email],
        help_text=_('It must be an @itba.edu.ar email address.')
    )

    STUDENT = 'S'
    STAFF = 'F'
    EX_STUDENTS = 'E'
    EXCHANGE = 'X'

    MEMBER_TYPES = (
        (STUDENT, _('Student')),
        (STAFF, _('Staff')),
        (EX_STUDENTS, _('Ex Student')),
        (EXCHANGE, _('Exchange'))
    )

    type = models.CharField(
        verbose_name=_('type'),
        max_length=1,
        choices=MEMBER_TYPES,
        default=STUDENT
    )

    dni = models.CharField(
        verbose_name='DNI',
        max_length=10,
        default='',
        blank=True,
        db_index=True
    )

    objects = models.Manager()
    active = ActiveStudentModelManager()

    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')
        permissions = (
            ('save_student', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return self.name

    def is_active(self):
        return Student.active.filter(student_id=self.student_id).count() == 1

    is_active.short_description = _("active")
    is_active.boolean = True

    def save(self, *args, **kwargs):
        """
        Al crear un estudiante, automaticamente asignarle el servicio del CEITBA
        """

        add_ceitba_enrollment = kwargs.pop('add_ceitba_enrollment', True)
        auto_bill = kwargs.pop('auto_bill', False)

        is_new = self.pk is None

        logger.info("Guardando datos del estudiante: %s", self)
        super(Student, self).save(*args, **kwargs)

        if is_new and add_ceitba_enrollment:
            ceitba_service = Service.objects.get(name=config.CEITBA_SERVICE_NAME)
            enrollment = Enrollment(student=self, service=ceitba_service)

            if self.type == Student.STAFF:
                enrollment.billable = auto_bill
            elif self.type == Student.EXCHANGE or self.type == Student.EX_STUDENTS:
                enrollment.billable = False

            enrollment.save()

            logger.info("Estudiante nuevo, dando de alta en el CEITBA. %s", enrollment)

    def delete(self, *args, **kwargs):
        """
        En lugar de borrar un producto, asignarle 'date_removed' a la fecha actual
        """
        self.date_removed = date.today()
        self.save()

        logger.info("Dando de baja al estudiante %s. Marcando como removido de la base de datos", self)


class Service(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=200,
        db_index=True,
        unique=True
    )
    price = models.DecimalField(
        verbose_name=_('price'),
        max_digits=8,
        decimal_places=2
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )
    date_removed = models.DateField(
        verbose_name=_('date removed'),
        null=True,
        blank=True,
        db_index=True
    )
    single_subscription = models.BooleanField(
        verbose_name=_('single subscription'),
        help_text=_('Unmark this box to allow more than one subscription per member'),
        default=True,
        db_index=True
    )

    LOCKER = 'L'
    LANGUAGE_COURSE = 'C'
    NONE = 'N'

    SERVICE_TYPES = (
        (NONE, _('None')),
        (LOCKER, _('Locker')),
        (LANGUAGE_COURSE, _('Language Course')),
    )
    type = models.CharField(
        verbose_name=_('type'),
        choices=SERVICE_TYPES,
        max_length=1,
        default=NONE
    )

    objects = models.Manager()
    active = ActiveModelManager()

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        permissions = (
            ('save_service', 'NEW: Can save changes made to the model'),
        )
        ordering = ['name']

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        """
        En lugar de borrar un servicio, asignarle 'date_removed' a la fecha actual
        """
        self.date_removed = date.today()
        self.save()

        logger.info("Servicio %s dado de baja.", self)

        # Marcar a los alumnos susciptos a este servicio como dados de baja
        for enrollment in self.enrollment_set.all():
            logger.info("Dando de baja en cascada la suscripcion %s", enrollment)
            enrollment.delete()


class Product(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=200
    )
    price = models.DecimalField(
        verbose_name=_('price'),
        max_digits=8,
        decimal_places=2
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )
    date_removed = models.DateField(
        verbose_name=_('date removed'),
        null=True,
        blank=True,
        db_index=True
    )
    track_inventory = models.BooleanField(
        verbose_name='registrar inventario',
        default=False
    )
    minimum_stock = models.PositiveIntegerField(
        verbose_name='stock minimo',
        blank=True,
        null=True,
        default=None
    )

    objects = models.Manager()
    active = ActiveModelManager()

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        permissions = (
            ('save_product', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return "%s - $%s" % (self.name, self.price)

    def delete(self, *args, **kwargs):
        """
        En lugar de borrar un producto, asignarle 'date_removed' a la fecha actual
        """
        self.date_removed = date.today()
        self.save()

        logger.info("Producto %s dado de baja.", self)

    def is_active(self):
        return self.date_removed is None

    def inventory(self):
        return self.inventoryentry_set.filter(acquired=True).aggregate(quantity=Coalesce(Sum('quantity'), 0))[
            'quantity']

    def clean(self):
        super(Product, self).clean()

        if self.track_inventory:
            MinValueValidator(1)(self.minimum_stock)

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        if is_new:
            older_products = Product.active.filter(name=self.name)

            if older_products.count() == 1:
                product = older_products.get()
                product.date_removed = date.today()
                super(Product, product).save(*args, **kwargs)
                super(Product, self).save(*args, **kwargs)

                from informacion.models import InventoryEntry

                InventoryEntry.objects.filter(product=product).update(product=self)

                logger.info("Dando de baja producto %s con precio desactualizado para usar el nuevo.", product)

                return True

            elif older_products.count() != 0:
                logger.critical("More than one activated product exists.")
                return False
            else:
                super(Product, self).save(*args, **kwargs)
        else:
            super(Product, self).save(*args, **kwargs)

        return False

    def consume_inventory(self, quantity: int):

        if not self.track_inventory:
            return

        inventory_entries = self.inventoryentry_set.filter(quantity__gt=0, acquired=True).order_by('date_created')

        if not inventory_entries.exists():
            return

        inventory_available = inventory_entries.aggregate(quantity=Coalesce(Sum('quantity'), 0))['quantity']

        if quantity > inventory_available:
            raise Exception('Inventory not enough')

        for inventory_entry in inventory_entries.reverse():
            consumed = min(inventory_entry.quantity, quantity)

            quantity -= consumed
            logger.info("Consuming inventory. %s. InventoryEntry: %s, Consumed: %d", self, inventory_entry, consumed)

            inventory_entry.quantity -= consumed
            inventory_entry.save()

            if quantity == 0:
                break

        if config.INVENTORY_NOTIFICATIONS and self.track_inventory and self.inventory() < self.minimum_stock:
            subject = 'Facturación CEITBA: Aviso de stock!'

            context = {
                'product': self,
            }

            html_content = render_to_string('facturacion/emails/stock_notification.html', context)

            to = [config.CEITBA_EMAIL]

            msg = EmailMessage(
                subject=subject,
                body=html_content,
                to=to)
            msg.content_subtype = "html"
            try:
                msg.send()
            except Exception as e:
                logger.exception("Failed to send email. to=%s", str(to))


class Report(models.Model):
    date_created = models.DateField(
        verbose_name=_('to date'),
        default=date.today
    )
    totalin = models.DecimalField(
        verbose_name=_('total earnings'),
        max_digits=8,
        decimal_places=2
    )
    totalout = models.DecimalField(
        verbose_name=_('total losses'),
        max_digits=8,
        decimal_places=2
    )
    report_file = models.FileField(
        verbose_name=_('report file'),
        upload_to='reports/'
    )
    report_staff_file = models.FileField(
        verbose_name=_('staff report file'),
        upload_to='reports/',
        null=True
    )
    report_accounting_file = models.FileField(
        verbose_name='Reporte de tesorería',
        upload_to='reports/',
        null=True
    )
    students = models.PositiveIntegerField(
        verbose_name=_("students count"),
        default=0
    )
    active_members = models.PositiveIntegerField(
        verbose_name=_("active members"),
        default=0
    )
    subscriptions = models.PositiveIntegerField(
        verbose_name=_("subscriptions"),
        default=0
    )
    unsubscriptions = models.PositiveIntegerField(
        verbose_name=_("unsubscriptions"),
        default=0
    )

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        get_latest_by = "date_created"
        permissions = (
            ('save_report', 'NEW: Can save changes made to the model'),
        )

    @transaction.atomic
    def save(self, *args, **kwargs):

        from informacion.models import PrinterCount, PrintingException, YMCAFamilyMember
        from facturacion.export import generate_spreadsheet as generate_spreadsheet, generate_totals, \
            export_accounting_data

        is_new = self.pk is None

        if is_new:

            try:
                start_date = Report.objects.latest().date_created
            except Report.DoesNotExist:
                start_date = datetime.date(2000, 1, 1)

            logger.info("Creando nuevo reporte desde el %s", start_date)

            product = Product.active.get(name=config.IMPRESIONES_PRODUCT)

            print_count_objects = PrinterCount.objects.filter(
                print_count__gt=config.IMPRESIONES_GRATIS,
            )

            for print_count in print_count_objects.iterator():

                # TODO Excepciones a impresiones
                # excepciones = PrintingException.objects.filter(member=student).filter(
                #     date__gte=from_date,
                #     date__lt=to_date
                # ).aggregate(total_pages=Sum('count'))['total_pages'] or 0
                #
                # if excepciones >= impresiones:k
                #     continue
                #
                # impresiones -= excepciones

                prints_to_charge = print_count.print_count

                # Se puede optimizar con un subquery
                if print_count.member.is_active():
                    prints_to_charge = print_count.print_count - config.IMPRESIONES_GRATIS

                purchase = Purchase(student=print_count.member)
                purchase.save()

                item = PurchaseItem(product=product, quantity=prints_to_charge, purchase=purchase)
                item.save()

            ymca_familymember_product = Product.active.get(name=config.YMCA_FAMILYMEMBER_PRODUCT)

            for ymca_familymember_entry in YMCAFamilyMember.objects.all():
                submembers = len(ymca_familymember_entry.family_members.splitlines())

                purchase = Purchase(student=ymca_familymember_entry.enrollment.student)
                purchase.save()

                item = PurchaseItem(product=ymca_familymember_product, quantity=submembers, purchase=purchase)
                item.save()

            students_file_obj = generate_spreadsheet([Student.STUDENT])
            staff_file_obj = generate_totals(Student.STAFF)

            self.totalin = Enrollment.active.aggregate(earnings=Sum('service__price'))['earnings']

            self.totalin += Purchase.objects.filter(
                reported_in__isnull=True
            ).aggregate(
                total=Coalesce(
                    Sum(
                        F('purchaseitem__product__price') * F('purchaseitem__quantity'),
                        output_field=DecimalField(max_digits=8, decimal_places=2)
                    ), 0)
            )['total']

            self.totalin += SpecialPurchase.objects.filter(
                reported_in__isnull=True
            ).aggregate(
                total=Coalesce(
                    Sum(F('amount') * F('quantity'),
                        output_field=DecimalField(max_digits=8, decimal_places=2)
                        ), 0)
            )['total']

            self.totalout = Enrollment.objects.filter(reported_in__isnull=False,
                                                      date_removed__isnull=False,
                                                      reported_in2__isnull=True).aggregate(
                earnings=Coalesce(Sum('service__price'), 0)
            )['earnings']

            self.students = Student.objects.filter(type=Student.STUDENT).count()
            self.active_members = Student.active.filter(type=Student.STUDENT).count()

            self.subscriptions = Enrollment.active.filter(
                service__name=config.CEITBA_SERVICE_NAME,
                reported_in__isnull=True,
                student__type=Student.STUDENT
            ).count()

            self.unsubscriptions = Enrollment.objects.filter(
                service__name=config.CEITBA_SERVICE_NAME,
                date_removed__isnull=False,
                reported_in2__isnull=True,
                student__type=Student.STUDENT
            ).count()

            file_name = "Facturacion %s %s a %s.xlsx" % ('ALUMNOS', start_date, date.today())
            students_file_obj.seek(0)
            self.report_file.save(file_name, ContentFile(students_file_obj.getvalue()), save=False)

            file_name = "Facturacion %s %s a %s.xlsx" % ('PERSONAL', start_date, date.today())
            staff_file_obj.seek(0)
            self.report_staff_file.save(file_name, ContentFile(staff_file_obj.getvalue()), save=False)

            accounting_file_obj = export_accounting_data()
            file_name = "Reporte Tesoreria %s a %s.xlsx" % (start_date, date.today())
            accounting_file_obj.seek(0)
            self.report_accounting_file.save(file_name, ContentFile(accounting_file_obj.getvalue()), save=False)

            logger.info("Reporte ALUMNOS creado en %s. Reporte PERSONAL creado en %s", self.report_file.path,
                        self.report_staff_file.path)

        super(Report, self).save(*args, **kwargs)

        if is_new:

            not_billable = Student.active.filter(enrollment__billable=False).distinct()

            for student in not_billable:

                logger.info('Adding debts to student: %s', student)

                enrollments = student.enrollment_set.filter(billable=False,
                                                            date_removed__isnull=True)

                if not enrollments.exists():
                    continue

                debt = Debt(student=student, from_report=self)
                debt.save()

                for enrollment in enrollments:
                    logger.info('Adding enrollment to last debt: %s', enrollment)
                    debt.enrollments.add(enrollment)

            # Marcamos las compras como reportadas
            Purchase.objects.filter(reported_in__isnull=True).update(reported_in=self)
            SpecialPurchase.objects.filter(reported_in__isnull=True).update(reported_in=self)

            # Marcamos los reembolsos como reportados
            Reimbursement.objects.filter(reported_in__isnull=True).update(reported_in=self)

            # Marcamos las altas como reportadas
            Enrollment.objects.filter(reported_in__isnull=True,
                                      date_removed__isnull=True).update(reported_in=self)

            # Marcamos las bajas como reportadas
            Enrollment.objects.filter(reported_in__isnull=False,
                                      date_removed__isnull=False,
                                      reported_in2__isnull=True).update(reported_in2=self)

            PrinterCount.objects.update(print_count=0)

    def __str__(self):
        return 'Reporte del %s al %s' % (Report.objects.exclude(id=self.id).latest().date_created, self.date_created)


class Enrollment(models.Model):
    """
    Los enrollments tienen 4 estados posibles:
        1. reported_in = None   : Fue creado, pero aun no se ha reportado.

        2. reported_in != None  : Fue reportado, pero aun no fue dado de baja
           date_removed = None

        3. date_removed != None : Fue dado de baja, pero aun no fue reportada
           reported_in2 = None

        4. reported_in2 != None : La baja ya fue reportada
    """

    student = models.ForeignKey(
        to=Student,
        verbose_name=_("student"),
        db_index=True
    )
    service = models.ForeignKey(
        to=Service,
        verbose_name=_("service"),
        db_index=True
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )
    date_removed = models.DateField(
        verbose_name=_('date removed'),
        null=True,
        blank=True,
        db_index=True
    )
    reported_in = models.ForeignKey(  # Reporte de alta
        to=Report,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    reported_in2 = models.ForeignKey(  # Reporte de baja
        to=Report,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reported_in2'
    )
    billable = models.BooleanField(
        verbose_name=_('billable'),
        default=True,
        help_text=_("Unmark if this enrollment shouldn't be included in a report.")
    )

    objects = models.Manager()
    active = ActiveModelManager()

    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        permissions = (
            ('save_enrollment', 'NEW: Can save changes made to the model'),
        )

    def is_active(self):
        return self.date_removed is None

    is_active.short_description = _("active")
    is_active.boolean = True

    def _student_id(self):
        return self.student.student_id

    def __str__(self):
        return '%s @ %s' % (self.student, self.service)

    _student_id.short_description = _('id')
    property(_student_id)

    def clean(self):

        is_new = self.pk is None

        if is_new:

            # Servicios a los que esta suscripto el estudiante que estan activos
            services = Enrollment.active.filter(
                student=self.student,
                service=self.service,
                service__date_removed__isnull=True,
                service__single_subscription=True
            )

            if services.count() > 0:
                raise ValidationError(_("The user is already subscribed to the service."), code='invalid')

    def delete(self, *args, **kwargs):
        """
        Al borrar una suscripcion, asignarle 'date_removed' a la fecha actual
        Si se esta borrando el servicio del CEITBA, borrar en cascada el resto de los servicios del alumno.
        """

        self.date_removed = date.today()

        # Si se dio de alta y baja en el mismo ciclo, eliminar la suscripcion
        if self.reported_in is None:
            logger.info("Dando de baja la suscripcion %s. Alta y baja en el mismo ciclo, eliminando realmente.", self)
            super(Enrollment, self).delete()
        else:
            logger.info("Suscripcion %s dada de baja.", self)
            self.save(delete=True)

        if self.service.type == Service.LOCKER:
            from lockers.models import LockerAssignation

            assignations = LockerAssignation.objects.filter(enrollment=self)

            if assignations.exists():
                assignations.get().delete(delete_enrollment=False)

        if self.service.name == config.CEITBA_SERVICE_NAME:
            logger.info("El alumno se dio de baja del CEITBA, dando de baja las suscripciones en cascada.")

            # Servicios a lo que esta suscripto el alumno que no se llamen CEITBA
            enrollments = Enrollment.active.filter(
                student=self.student
            ).exclude(
                service__name=config.CEITBA_SERVICE_NAME
            )

            for enrollment in enrollments:
                logger.info("Dando de baja %s por haberse desanotado del CEITBA", enrollment)
                enrollment.delete()

    def save(self, *args, **kwargs):
        """
        Al guardar una suscripcion, si no es el servicio del CEITBA, y no se esta borrando la suscripcion,
        dar de alta al estudiante en el servicio del CEITBA
        """
        delete = kwargs.pop('delete', False)
        add_ymca_medical_exam = kwargs.pop('add_ymca_medical_exam', False)

        super(Enrollment, self).save(*args, **kwargs)
        if not delete:
            logger.info("Creando suscripcion %s", self)

        if not delete and self.service.name != config.CEITBA_SERVICE_NAME:

            ceitba_service = Service.objects.get(name=config.CEITBA_SERVICE_NAME)

            # Servicios a los que esta suscripto el alumno que se llamen CEITBA y esten activos
            not_ceitba_enrollments = Enrollment.active.filter(student=self.student,
                                                              service=ceitba_service)

            # Si no esta suscripto al CEITBA suscribirlo
            if not_ceitba_enrollments.count() == 0:
                logger.info("Suscripcion creada sin ser socio del CEITBA, suscribiendo.")
                enrollment = Enrollment(student=self.student, service=ceitba_service, billable=self.billable)
                enrollment.save()

        if add_ymca_medical_exam and self.service.name == config.YMCA_SERVICE_NAME:
            # Se tiene que agregar una compra para el examen medico del YMCA

            purchase = Purchase(student=self.student)
            purchase.save()

            medicalexam_product = Product.active.filter(name=config.YMCA_MEDICALEXAM_PRODUCT_NAME).get()

            logger.info("Al alumno %s se le cobrará el examen médico (%d) en la próxima facturación.",
                        purchase.student, medicalexam_product.price)

            medicalexam = PurchaseItem(purchase=purchase, quantity=1)
            medicalexam.product = medicalexam_product
            medicalexam.save()


class Purchase(models.Model):
    student = models.ForeignKey(
        to=Student,
        verbose_name=_("student"),
        db_index=True
    )
    date_created = models.DateField(
        verbose_name=_("date"),
        default=date.today,
        db_index=True
    )
    reported_in = models.ForeignKey(
        to=Report,
        null=True,
        on_delete=models.SET_NULL
    )
    billable = models.BooleanField(
        verbose_name='facturar',
        help_text='Desmarquelo para un pago en efectivo',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = _('Purchase')
        verbose_name_plural = _('Purchases')
        permissions = (
            ('save_purchase', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return "Compra de %s" % self.student.name


class CashPurchase(models.Model):
    student = models.ForeignKey(
        to=Student,
        verbose_name=_("student"),
        db_index=True
    )
    date_created = models.DateField(
        verbose_name=_("date"),
        default=date.today,
        db_index=True
    )

    class Meta:
        verbose_name = 'Compra en Efectivo'
        verbose_name_plural = 'Compras en Efectivo'
        permissions = (
            ('save_cashpurchase', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return "Compra de %s" % self.student.name


class CashPurchaseItem(models.Model):
    purchase = models.ForeignKey(
        to=CashPurchase
    )
    product = models.ForeignKey(
        to=Product,
        verbose_name=_('product')
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('quantity'),
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = _('Cash Purchase Item')
        verbose_name_plural = _('Cash Purchase Items')
        permissions = (
            ('save_cashpurchaseitem', 'NEW: Can save changes made to the model'),
        )

    def clean(self):
        is_new = self.pk is None

        if is_new:
            try:
                if self.product.track_inventory and self.quantity > self.product.inventory():
                    raise ValidationError('Inventario insuficiente para realizar la compra', code='invalid')
            except Product.DoesNotExist:
                pass

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super(CashPurchaseItem, self).save(*args, **kwargs)

        if is_new:
            self.product.consume_inventory(self.quantity)

    def __str__(self):
        return "%d %s por %s" % (self.quantity, self.product, self.purchase.student)


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        to=Purchase
    )
    product = models.ForeignKey(
        to=Product,
        verbose_name=_('product')
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('quantity'),
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = _('Purchase Item')
        verbose_name_plural = _('Purchase Items')
        permissions = (
            ('save_purchaseitem', 'NEW: Can save changes made to the model'),
        )

    def clean(self):
        is_new = self.pk is None

        if is_new:
            try:
                if self.product.track_inventory and self.quantity > self.product.inventory():
                    raise ValidationError('Inventario insuficiente para realizar la compra', code='invalid')
            except Product.DoesNotExist:
                pass

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super(PurchaseItem, self).save(*args, **kwargs)

        if is_new:
            self.product.consume_inventory(self.quantity)

    def __str__(self):
        return "%d %s por %s" % (self.quantity, self.product, self.purchase.student)


class Reimbursement(models.Model):
    student = models.ForeignKey(
        to=Student,
        verbose_name=_("student")
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )
    concept = models.TextField(
        verbose_name=_('concept'),
        max_length=500,
        blank=True
    )
    amount = models.DecimalField(
        verbose_name=_('amount'),
        max_digits=8,
        decimal_places=2
    )
    reported_in = models.ForeignKey(
        to=Report,
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _('Reimbursement')
        verbose_name_plural = _('Reimbursements')
        get_latest_by = "date_created"
        permissions = (
            ('save_reimbursement', 'NEW: Can save changes made to the model'),
        )


class DebtManager(models.Manager):
    """
    Manager que solo devuelve los objetos que no fueron dados de baja en el queryset.
    """

    def get_queryset(self):
        return super(DebtManager, self).get_queryset().select_related('student').prefetch_related('enrollments',
                                                                                                  'enrollments__service',
                                                                                                  'enrollments__student') \
            .annotate(amount=Coalesce(Sum('enrollments__service__price'), 0))


class Debt(models.Model):
    student = models.ForeignKey(
        to=Student,
        verbose_name=_("student")
    )
    enrollments = models.ManyToManyField(
        to=Enrollment,
        verbose_name=_('enrollments')
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )
    date_paid = models.DateField(
        verbose_name=_("date paid"),
        default=None,
        null=True,
        blank=True,
        db_index=True
    )
    from_report = models.ForeignKey(
        to=Report,
        verbose_name=_('from report'),
        null=True,
        default=None,
        on_delete=models.CASCADE
    )
    bill = models.FileField(
        verbose_name='comprobante',
        upload_to='comprobantes',
        null=True,
        default=None,
        blank=True,
    )

    @property
    def is_paid(self):
        return self.date_paid is not None

    objects = DebtManager()

    def __str__(self):
        return _('Debt from %(from)s.') % {'from': self.student}

    class Meta:
        verbose_name = _('Debt')
        verbose_name_plural = _('Debts')
        permissions = (
            ('save_debt', 'NEW: Can save changes made to the model'),
        )


class Gift(models.Model):
    member = models.ForeignKey(
        to=Student,
        verbose_name='miembro'
    )
    product = models.ForeignKey(
        to=Product
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('quantity'),
        validators=[MinValueValidator(1)]
    )
    concept = models.TextField(
        verbose_name=_('concept'),
        max_length=500
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )

    class Meta:
        verbose_name = 'Regalo'
        verbose_name_plural = 'Regalos'
        permissions = (
            ('save_gift', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return "%d %s a %s" % (self.quantity, self.product.name, self.member.name)

    def clean(self):
        is_new = self.pk is None

        if is_new:

            try:
                if self.product.track_inventory and self.quantity > self.product.inventory():
                    raise ValidationError('Inventario insuficiente para realizar el regalo', code='invalid')
            except Product.DoesNotExist:
                pass

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super(Gift, self).save(*args, **kwargs)

        if is_new:
            self.product.consume_inventory(self.quantity)


class SpecialPurchase(models.Model):
    member = models.ForeignKey(
        to=Student,
        verbose_name='miembro',
    )
    date_created = models.DateField(
        verbose_name=_("date"),
        default=date.today,
        db_index=True
    )
    reported_in = models.ForeignKey(
        to=Report,
        null=True,
        on_delete=models.SET_NULL
    )
    billable = models.BooleanField(
        verbose_name='facturar',
        help_text='Desmarquelo para un pago en efectivo',
        default=True,
        db_index=True
    )
    product = models.ForeignKey(
        to=Product,
        verbose_name=_('product')
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('quantity'),
        validators=[MinValueValidator(1)]
    )
    amount = models.DecimalField(
        verbose_name='monto',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    concept = models.TextField(
        verbose_name='concepto'
    )

    class Meta:
        verbose_name = 'Compra Especial'
        verbose_name_plural = 'Compras Especiales'
        permissions = (
            ('save_specialpurchase', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return "Compra de %s %s a $%s para %s" % (self.quantity, self.product.name, self.amount, self.member.name)

    def clean(self):

        is_new = self.pk is None

        if is_new:

            try:
                if self.product.track_inventory and self.quantity > self.product.inventory():
                    raise ValidationError('Inventario insuficiente', code='invalid')
            except Product.DoesNotExist:
                pass

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super(SpecialPurchase, self).save(*args, **kwargs)

        if is_new:
            self.product.consume_inventory(self.quantity)


class Change(models.Model):
    purchaseitem = models.ForeignKey(
        to=PurchaseItem,
        verbose_name='item de compra'
    )
    new_product = models.ForeignKey(
        to=Product
    )

    def clean(self):
        super(Change, self).clean()

        if self.purchaseitem.product.price != self.new_product.price:
            raise ValidationError('El precio del nuevo producto debe coincidir con el anterior.')

    def save(self, *args, **kwargs):
        super(Change, self).save(*args, **kwargs)


class Bill(models.Model):
    FACTURA = 'f'
    TICKET = 't'

    BILL_TYPES = (
        (FACTURA, 'Factura'),
        (TICKET, 'Ticket'),
    )
    type = models.CharField(
        verbose_name='Tipo',
        max_length=1,
        db_index=True,
        choices=BILL_TYPES
    )

    AGRUPACIONES = 'a'
    DEPORTES = 'd'
    GASTOS_EXC = 'g'

    GIMNASIO = 'o'
    IDIOMAS = 'i'
    INTERNACIONALES = 't'
    LACOPIA = 'l'
    LABORATORIO = 'p'
    NAUTICA = 'n'
    OFICINA = 'f'
    SERVICIOS = 's'

    DEPARTAMENTOS = (
        (AGRUPACIONES, 'Agrupaciones'),
        (DEPORTES, 'Deportes'),
        (GASTOS_EXC, 'Gastos Excepcionales'),
        (GIMNASIO, 'Gimnasio'),
        (IDIOMAS, 'Idiomas'),
        (INTERNACIONALES, 'Internacionales'),
        (LACOPIA, 'La Copia'),
        (LABORATORIO, 'Laboratorio'),
        (NAUTICA, 'Nautica'),
        (OFICINA, 'Oficina'),
        (SERVICIOS, 'Servicios')

    )

    departamento = models.CharField(
        verbose_name='Departamento',
        choices=DEPARTAMENTOS,
        db_index=True,
        max_length=1
    )

    concepto = models.CharField(
        verbose_name='Concepto',
        max_length=300
    )

    descripcion = models.CharField(
        verbose_name='Descripcion',
        max_length=300
    )

    monto = models.DecimalField(
        verbose_name='Monto',
        max_digits=8,
        decimal_places=2
    )

    month = models.PositiveSmallIntegerField(
        verbose_name='Mes',
        choices=MONTHS.items(),
        db_index=True
    )

    year = models.PositiveSmallIntegerField(
        verbose_name='Ano',
        default=datetime.date.today().year
    )

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        permissions = (
            ('save_bill', 'NEW: Can save changes made to the model'),
        )

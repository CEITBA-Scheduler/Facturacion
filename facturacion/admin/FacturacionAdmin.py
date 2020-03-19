import logging
from datetime import date

from constance import config
from constance.admin import ConstanceAdmin, Config
from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from bar import admin as bar_admin, models as bar_model
from contrib import MemberSearchWidget
from eventos import admin as eventos_admin, models as eventos_models
from facturacion import admin as facturacion_admin, models as facturacion_models
from facturacion.export import export_service, export_lockersite, exportar_altas_y_bajas, export_event
from informacion import admin as informacion_admin, models as informacion_models
from lockers import admin as lockers_admin, models as lockers_models
from nautica.admin import AuthorizationAdmin
from nautica.models import Authorization

if not settings.DEBUG:
    from datadog import statsd

logger = logging.getLogger(__name__)


class RangeForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=facturacion_models.Service.active.all(),
        label='Servicio'
    )

    start = forms.DateField(label='Fecha inicio', help_text='Ejemplo: 01/01/2017')
    end = forms.DateField(label='Fecha fin', help_text='Ejemplo: 01/01/2017')


class SearchForm(forms.Form):
    member_id = forms.CharField(
        label='Legajo',
        widget=MemberSearchWidget
    )


class PrintReportForm(forms.Form):
    file = forms.FileField(
        label="Archivo de Reporte"
    )


class FacturacionAdmin(AdminSite):
    site_header = 'Facturación CEITBA'

    site_title = 'Facturación'

    index_title = 'CEITBA'

    site_url = None

    def get_urls(self):
        urls = super(FacturacionAdmin, self).get_urls()
        my_urls = [
            url(r'^export$', self.admin_view(self.export_service), name='export_service'),
            url(r'^export_event$', self.admin_view(self.export_event), name='export_event'),
            url(r'^export_lockersite$', self.admin_view(self.export_lockersite), name='export_lockersite'),
            url(r'^export_service_range$', self.admin_view(self.export_service_range), name='export_service_range'),
            url(r'^impresiones$', self.admin_view(self.printing_count_view), name='impresiones'),
            url(r'^gimnasio', self.admin_view(self.gym_member_view), name='gym_member_view'),
            url(r'^print_report', self.admin_view(self.print_report), name='print_report'),
        ]
        return my_urls + urls

    def export_service(self, request):

        if not request.method == 'GET':
            return HttpResponseNotAllowed(_('Invalid HTTP method'))

        if 'service' not in request.GET:
            return HttpResponseBadRequest(_("Missing service parameter."))

        service = facturacion_models.Service.objects.filter(name__exact=request.GET['service'])

        if not service.exists():
            return HttpResponseBadRequest(_("Service does not exist"))

        service = service.get()

        file_obj = export_service(service)
        file_obj.seek(0)
        # generate the file
        response = HttpResponse(
            file_obj.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response['Content-Disposition'] = 'attachment; filename=Alumnos activos en %s al %s.xlsx' % (
            urlquote(service.name),
            date.today()
        )
        return response

    def export_lockersite(self, request):

        if not request.method == 'GET':
            return HttpResponseNotAllowed(_('Invalid HTTP method'))

        if 'lockersite' not in request.GET:
            return HttpResponseBadRequest(_("Missing lockersite parameter."))

        lockersites = lockers_models.LockerSite.objects.filter(pk=request.GET['lockersite'])

        if not lockersites.exists():
            return HttpResponseBadRequest(_("Locker Site does not exist"))

        lockersite = lockersites.get()

        file_obj = export_lockersite(lockersite)
        file_obj.seek(0)
        # generate the file
        response = HttpResponse(
            file_obj.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response['Content-Disposition'] = 'attachment; filename=Alumnos con locker en %s al %s.xlsx' % (
            urlquote(lockersite.service.name),
            date.today()
        )
        return response

    def export_service_range(self, request):

        if request.method == 'GET':
            context = self.each_context(request)

            context['range_form'] = RangeForm()

            return render(request, 'admin/export_service_range.html', context)

        range_form = RangeForm(request.POST)

        if range_form.is_valid():
            file_obj = exportar_altas_y_bajas(range_form.cleaned_data['service'].name,
                                              range_form.cleaned_data['start'],
                                              range_form.cleaned_data['end'])
            file_obj.seek(0)
            # generate the file
            response = HttpResponse(
                file_obj.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            # TODO: Cambiar el nombre del archivo
            response['Content-Disposition'] = 'attachment; filename=Altas y bajas en %s del %s al %s.xlsx' % (
                urlquote(range_form.cleaned_data['service'].name),
                range_form.cleaned_data['start'],
                range_form.cleaned_data['end']
            )

            if not settings.DEBUG:
                statsd.increment("ceitba.service.export.count")

            return response

    def printing_count_view(self, request):

        if request.method == 'POST':

            search_form = SearchForm(request.POST)

            if search_form.is_valid():
                member = facturacion_models.Student.objects.get(pk=search_form.cleaned_data['member_id'])

                context = self.each_context(request)
                context['member'] = member
                context['prints'] = informacion_models.PrinterCount.objects.get(member=member).print_count

                if not settings.DEBUG:
                    statsd.increment("ceitba.printing.search.count")

                return render(request, 'admin/printing_count_result.html', context)

        else:
            search_form = SearchForm()

        context = self.each_context(request)

        context['search_form'] = search_form

        context['total'] = informacion_models.PrinterCount.objects.aggregate(total=Sum('print_count'))['total']

        return render(request, 'admin/printing_count_search.html', context)

    def gym_member_view(self, request):

        if request.method == 'POST':

            search_form = SearchForm(request.POST)

            if search_form.is_valid():
                member = facturacion_models.Student.objects.get(pk=search_form.cleaned_data['member_id'])

                context = self.each_context(request)
                context['member'] = member

                context['enrollment_within_range'] = False

                enrollment = facturacion_models.Enrollment.active.filter(
                    student=member,
                    service__name=config.GIMNASIO_SERVICE_NAME
                )

                if enrollment.exists():
                    context['is_enrolled'] = True
                    context['enrollment_within_range'] = (
                                                                 date.today() - enrollment.get().date_created).days < config.GIMNASIO_GRACE_PERIOD

                context['certificate_valid'] = False

                certificate = informacion_models.SportCertificate.objects.filter(member=member)

                if certificate.exists():
                    context['certificate_valid'] = informacion_models.SportCertificate.objects.filter(
                        member=member).latest().is_valid()

                if not settings.DEBUG:
                    statsd.increment("ceitba.gym.search.count")

                return render(request, 'admin/gym_member_result.html', context)

        else:
            search_form = SearchForm()

        context = self.each_context(request)

        context['search_form'] = search_form

        return render(request, 'admin/gym_member_search.html', context)

    def export_event(self, request):

        if not request.method == 'GET':
            return HttpResponseNotAllowed(_('Invalid HTTP method'))

        if 'event' not in request.GET:
            return HttpResponseBadRequest(_("Missing service parameter."))

        event = eventos_models.Event.objects.filter(id=request.GET['event'])

        if not event.exists():
            return HttpResponseBadRequest(_("Event does not exist"))

        event = event.get()

        file_obj = export_event(event)
        file_obj.seek(0)
        # generate the file
        response = HttpResponse(
            file_obj.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response['Content-Disposition'] = 'attachment; filename=Miembros inscriptos en %s al %s.xlsx' % (
            urlquote(event.name),
            date.today()
        )
        return response

    def print_report(self, request):

        if request.method == 'POST':

            print_report_form = PrintReportForm(request.POST, request.FILES)

            if print_report_form.is_valid():

                context = {}

                file = request.FILES['file']

                _ = file.readline()  # brand
                _ = file.readline()  # header

                import csv

                pages = 0

                while True:
                    line = file.readline()
                    line = line.strip()
                    if not line:
                        break

                    parsed_line = csv.reader([line.decode("latin1")])
                    data = list(parsed_line)[0]

                    try:
                        legajo = int(data[1])
                        paginas = int(data[2])
                    except:
                        continue

                    pages += paginas

                context['pages'] = pages

                return render(request, 'admin/printing_count_report_result.html', context)

        else:
            print_report_form = PrintReportForm()

        context = self.each_context(request)

        context['print_report_form'] = print_report_form

        return render(request, 'admin/printing_count_report.html', context)


facturacionadmin = FacturacionAdmin(name='Facturación CEITBA')

# Modelos del sistema de facturacion
facturacionadmin.register(facturacion_models.Product, facturacion_admin.ProductAdmin)
facturacionadmin.register(facturacion_models.Enrollment, facturacion_admin.EnrollmentAdmin)
facturacionadmin.register(facturacion_models.Service, facturacion_admin.ServiceAdmin)
facturacionadmin.register(facturacion_models.Purchase, facturacion_admin.PurchaseAdmin)
facturacionadmin.register(facturacion_models.CashPurchase, facturacion_admin.CashPurchaseAdmin)
facturacionadmin.register(facturacion_models.Student, facturacion_admin.StudentAdmin)
facturacionadmin.register(facturacion_models.Report, facturacion_admin.ReportAdmin)
facturacionadmin.register(facturacion_models.Reimbursement, facturacion_admin.ReimbursementAdmin)
facturacionadmin.register(facturacion_models.Debt, facturacion_admin.DebtAdmin)
facturacionadmin.register(facturacion_models.Gift, facturacion_admin.GiftAdmin)
facturacionadmin.register(facturacion_models.SpecialPurchase, facturacion_admin.SpecialPurchaseAdmin)
facturacionadmin.register(facturacion_models.Bill, facturacion_admin.BillAdmin)

# Modelos del sistema de informacion
facturacionadmin.register(informacion_models.JournalEntry, informacion_admin.JournalEntryAdmin)
facturacionadmin.register(informacion_models.PrinterReport, informacion_admin.PrinterReportAdmin)
facturacionadmin.register(informacion_models.SportCertificate, informacion_admin.SportCertificateAdmin)
facturacionadmin.register(informacion_models.InventoryCategory, informacion_admin.InventoryCategoryAdmin)
facturacionadmin.register(informacion_models.InventoryEntry, informacion_admin.InventoryEntryAdmin)
facturacionadmin.register(informacion_models.YMCAFamilyMember, informacion_admin.YMCAFamilyMemberAdmin)
facturacionadmin.register(informacion_models.PrintingException, informacion_admin.PrintingExceptionAdmin)
facturacionadmin.register(informacion_models.PrinterCount, informacion_admin.PrinterCountAdmin)
facturacionadmin.register(informacion_models.AlquilerMate, informacion_admin.AlquilerMateAdmin)
facturacionadmin.register(informacion_models.MediaObject, informacion_admin.MediaObjectAdmin)
facturacionadmin.register(informacion_models.InventoryLocation, informacion_admin.InventoryLocationAdmin)
facturacionadmin.register(informacion_models.Lend, informacion_admin.LendAdmin)
facturacionadmin.register(informacion_models.Document, informacion_admin.DocumentAdmin)
facturacionadmin.register(informacion_models.Reminder, informacion_admin.ReminderAdmin)
facturacionadmin.register(informacion_models.RangedExport, informacion_admin.RangedExportAdmin)

# Modelos del sistema de lockers
facturacionadmin.register(lockers_models.LockerSite, lockers_admin.LockerSiteAdmin)
facturacionadmin.register(lockers_models.LockerAssignation, lockers_admin.LockerAssignationAdmin)
facturacionadmin.register(lockers_models.LockerQueue, lockers_admin.LockerQueueAdmin)
facturacionadmin.register(lockers_models.LockerHold, lockers_admin.LockerHoldAdmin)

# Modelos del sistema de nautica
facturacionadmin.register(Authorization, AuthorizationAdmin)

# Modelos del sistema del bar
facturacionadmin.register(bar_model.Menu, bar_admin.MenuAdmin)
facturacionadmin.register(bar_model.MenuDescription, bar_admin.MenuDescriptionAdmin)
facturacionadmin.register(bar_model.BarProduct, bar_admin.BarProductAdmin)

# Modelos del sistema de eventos
facturacionadmin.register(eventos_models.Event, eventos_admin.EventAdmin)
facturacionadmin.register(eventos_models.EventInscription, eventos_admin.EventInscriptionAdmin)

facturacionadmin.register(User, UserAdmin)
facturacionadmin.register(Group, GroupAdmin)
facturacionadmin.register(Site, SiteAdmin)

facturacionadmin.register([Config], ConstanceAdmin)

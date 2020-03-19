import datetime
import logging
from datetime import date
from locale import currency as pretty_currency

from constance import config
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin
from facturacion.models import Report

logger = logging.getLogger(__name__)


class ReportAdmin(CustomModelAdmin):
    readonly_fields = ['_get_start_date', 'date_created', 'totalin', 'totalout', 'report_file', 'report_staff_file',
                       'report_accounting_file', 'students', 'active_members', 'subscriptions', 'unsubscriptions']
    list_display_links = ['_get_start_date', 'date_created']

    def get_list_display(self, request):
        """
        Solo mostramos si fue reportado o no al administrador
        """
        ans = ['_get_start_date', 'date_created', 'students', 'active_members']

        if request.user.is_superuser:
            ans += ['earnings_with_dollar', 'losses_with_dollar']

        return ans

    def earnings_with_dollar(self, obj):
        return pretty_currency(obj.totalin, grouping=True)

    earnings_with_dollar.short_description = _("earnings")

    def losses_with_dollar(self, obj):
        return pretty_currency(obj.totalout, grouping=True)

    losses_with_dollar.short_description = _("losses")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_fieldsets(self, request, obj=None):
        """
        En caso de ser un reporte nuevo, solo mostrar el rango de fechas que abarca. Si
        es un reporte existente, mostrar mas datos acerca de el.
        """
        if obj:
            return (
                (None, {
                    'fields': (
                        '_get_start_date', 'date_created', 'report_file', 'report_staff_file', 'report_accounting_file')
                }),
                (_("Statistics"), {
                    'fields': ('students', 'active_members', 'subscriptions', 'unsubscriptions')
                }),
            )
        else:
            return (
                (None, {
                    'fields': ('_get_start_date', 'date_created')
                }),
            )

    def has_add_permission(self, request):
        """
        Solo permitimos agregar un reporte si estamos a mas de 28 dias del ultimo reporte y a menos de 3 dias del 20
        :param request:
        :return:
        """

        if request.user.is_superuser:
            return True

        # if not PrinterReport.has_uploaded_report_for_this_month():
        #     #messages.error(request, 'Debe subir el reporte de impresiones antes de poder facturar este mes!')
        #     return False

        try:
            last_report = Report.objects.latest().date_created
        except Report.DoesNotExist:
            last_report = datetime.date(2000, 1, 1)

        today = date.today()
        margin = datetime.timedelta(days=config.REPORT_ALLOW_IF_WITHIN_RANGE)

        is_within_range = (
            today - margin <= datetime.date(today.year, today.month, config.DAY_TO_SEND_REPORT) <= today + margin)

        days_since_last = (today - last_report).days

        has_permission = super(ReportAdmin, self).has_add_permission(request)

        return has_permission and is_within_range and days_since_last > config.REPORT_MIN_DISTANCE_IN_DAYS

    def _get_start_date(self, obj:Report):
        last_report = Report.objects.filter(date_created__lt=obj.date_created).latest()
        return date_format(last_report.date_created)

    _get_start_date.short_description = _("from date")

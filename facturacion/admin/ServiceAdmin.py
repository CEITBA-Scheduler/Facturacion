import logging
from locale import currency as pretty_currency

from django.core.urlresolvers import reverse
from django.db.models import F, DecimalField, ExpressionWrapper, Case, When, Count
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin
from contrib.listfilters import ActiveListFilter

logger = logging.getLogger(__name__)


class ServiceAdmin(CustomModelAdmin):
    search_fields = ['name']
    ordering = ['name']

    def get_list_display(self, request):
        ans = ['name', 'price_with_dollar', 'date_created', '_subs_count', 'type', 'single_subscription']

        if request.user.is_superuser:
            ans += ['_earnings', 'is_active']

        return ans + ['_export_link']

    def get_fields(self, request, obj=None):

        ans = ['name', 'price', 'type']

        if obj:
            ans += ['date_created', 'date_removed']

        return ans + ['single_subscription']

    def get_readonly_fields(self, request, obj=None):
        """
         Si el usuario es superuser permitirle modificar las fechas de creacion
         y de baja
         """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(ServiceAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj is not None:
            fields += ['name']

        if not request.user.is_superuser:
            fields += ['date_created', 'date_removed', 'type']

        return fields

    def get_list_filter(self, request):
        ans = ['single_subscription', 'type']

        if request.user.is_superuser:
            ans += [ActiveListFilter]

        return ans

    def price_with_dollar(self, obj):
        return pretty_currency(obj.price)

    price_with_dollar.short_description = _("price")

    def has_delete_permission(self, request, obj=None):
        return False

    def _subs_count(self, obj):
        return obj.subscriptors

    def get_queryset(self, request):

        qs = super(ServiceAdmin, self).get_queryset(request).annotate(
            subscriptors=Count(
                Case(
                    When(
                        enrollment__date_removed__isnull=True,
                        date_removed__isnull=True,
                        enrollment__service=F('id'),
                        then=1),
                ),
            )).annotate(
            earnings=ExpressionWrapper(F('subscriptors') * F('price'),
                                       output_field=DecimalField(max_digits=8, decimal_places=2))
        )

        if request.user.is_superuser:
            return qs
        return qs.filter(date_removed__isnull=True)

    def _earnings(self, obj):
        return pretty_currency(obj.earnings, grouping=True)

    _subs_count.short_description = _('suscribed')
    _earnings.short_description = _('earnings')

    def _export_link(self, obj):
        return mark_safe(
            '<a href="%s?service=%s">%s</a>' % (
                reverse('admin:export_service'),
                urlquote(obj.name),
                _('Export to Excel')
            )
        )

    _export_link.short_description = _('Export')

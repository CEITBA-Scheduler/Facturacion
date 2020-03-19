from django.contrib.admin import SimpleListFilter
from django.utils.http import urlquote, urlunquote
from django.utils.translation import ugettext_lazy as _

from facturacion.models import Service


class ActiveListFilter(SimpleListFilter):
    title = _('active')

    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes')),
            ('0', _('No')),
        )

    def queryset(self, request, queryset):

        if self.value() == '1':
            return queryset.filter(date_removed__isnull=True)
        elif self.value() == '0':
            return queryset.filter(date_removed__isnull=False)
        else:
            return queryset


class PaidDebtFilter(SimpleListFilter):
    title = _('is paid')

    parameter_name = 'is_paid'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes')),
            ('0', _('No')),
        )

    def queryset(self, request, queryset):

        if self.value() == '1':
            return queryset.filter(date_paid__isnull=False)
        elif self.value() == '0':
            return queryset.filter(date_paid__isnull=True)
        else:
            return queryset


class ActiveServiceListFilter(SimpleListFilter):
    title = _('service')

    parameter_name = 'service'

    def lookups(self, request, model_admin):
        """
        Solo mostrar los servicios activos en la lista de filtros.
        """
        qs = Service.active.order_by('name')

        for elem in qs:
            yield (urlquote(elem.name), elem.name)

    def queryset(self, request, queryset):

        if self.value():
            return queryset.filter(service__name=urlunquote(self.value()))
        else:
            return queryset

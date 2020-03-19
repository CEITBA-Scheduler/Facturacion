import logging
from locale import currency as pretty_currency

from contrib import CustomModelAdmin

logger = logging.getLogger(__name__)


class BillAdmin(CustomModelAdmin):
    list_display = ['id', 'type', 'departamento', 'concepto', 'descripcion', 'price_with_dollar', 'month', 'year']
    fields = ['type', 'departamento', 'concepto', 'descripcion', 'monto', 'month', 'year']

    list_filter = ['type', 'departamento', 'year']

    def price_with_dollar(self, obj):
        return pretty_currency(obj.monto)

    price_with_dollar.short_description = 'Monto'

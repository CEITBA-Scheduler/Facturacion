from locale import currency as pretty_currency

from bar.models import BarProduct
from contrib import CustomModelAdmin


class BarProductAdmin(CustomModelAdmin):
    list_display = ['name', 'sede', '_price', 'important']
    fields = ['name', 'sede', 'price', 'important']
    list_filter = ['sede', 'important']
    ordering = ['name']

    def _price(self, obj: BarProduct):
        return pretty_currency(obj.price)

    _price.short_description = 'precio'

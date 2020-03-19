from locale import currency as pretty_currency

from bar.models import Menu
from contrib import CustomModelAdmin


class MenuAdmin(CustomModelAdmin):
    list_display = ['name', 'sede', '_price', 'order']
    fields = ['name', 'price', 'sede', 'order']
    list_filter = ['sede']
    ordering = ['sede', 'order']

    def _price(self, obj: Menu):
        return pretty_currency(obj.price)

    _price.short_description = 'precio'

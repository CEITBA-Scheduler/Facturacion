from django.forms import ModelForm
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin
from facturacion.models import Product


class InventoryEntryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(InventoryEntryForm, self).__init__(*args, **kwargs)
        if 'product' in self.fields:
            self.fields['product'].queryset = Product.active.order_by('name')


class InventoryEntryAdmin(CustomModelAdmin):
    list_display = ['name', 'description', 'location', 'quantity', 'acquired']
    search_fields = ['description']
    list_filter = ['categories', 'location', 'acquired']
    form = InventoryEntryForm

    fieldsets = (
        ('General', {
            'fields': ('name', 'description', 'location', 'quantity', 'acquired')
        }),
        ('Categoría y libro diario', {
            'fields': ('categories', 'product'),
        }),
        ('Amortización', {
            'fields': ('original_value',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = super(InventoryEntryAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        return fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def _truncated_description(self, obj):
        return truncatechars(obj.description, 40)

    _truncated_description.short_description = _('description')

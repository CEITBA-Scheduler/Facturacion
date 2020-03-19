import logging

from django.forms import ModelForm

from contrib import MemberSearchWidget, CustomModelAdmin
from facturacion.models import Gift, Product

logger = logging.getLogger(__name__)


class GiftForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GiftForm, self).__init__(*args, **kwargs)
        if 'product' in self.fields:
            self.fields['product'].queryset = Product.active.order_by('name')

    class Meta:
        model = Gift
        fields = ['member', 'product', 'quantity', 'concept']
        widgets = {
            'member': MemberSearchWidget,
        }


class GiftAdmin(CustomModelAdmin):
    list_display = ['member', 'product', 'quantity', 'concept', 'date_created']
    fields = ['member', 'product', 'quantity', 'concept']
    ordering = ['date_created']
    form = GiftForm

    def get_readonly_fields(self, request, obj=None):
        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(GiftAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['member', 'product', 'quantity']

        return fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

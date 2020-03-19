import logging
from locale import currency as pretty_currency

from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from contrib import MemberSearchWidget, CustomModelAdmin
from facturacion.models import SpecialPurchase, Product

logger = logging.getLogger(__name__)


class SpecialPurchaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SpecialPurchaseForm, self).__init__(*args, **kwargs)
        if 'product' in self.fields:
            self.fields['product'].queryset = Product.active.order_by('name')

    class Meta:
        model = SpecialPurchase
        fields = ['member', 'product', 'quantity', 'amount', 'concept', 'billable']
        widgets = {
            'member': MemberSearchWidget,
        }


class SpecialPurchaseAdmin(CustomModelAdmin):
    ordering = ['-date_created']
    search_fields = ['member__name', 'member__student_id']
    list_display_links = ['get_student_id', 'member']
    date_hierarchy = 'date_created'
    list_filter = ['billable']
    form = SpecialPurchaseForm

    def get_list_display(self, request):
        """
        Solo mostramos si fue reportado o no al administrador
        """
        ans = ['get_student_id', 'member', '_total', 'date_created']

        if request.user.is_superuser:
            ans += ['is_reported']

        return ans

    def get_fields(self, request, obj=None):
        """
        Si estamos modificando un estudiante, mostrar un link a su pagina.
        """

        fields = ['product', 'quantity', 'amount', 'concept', 'billable']

        if obj:
            fields = ['_link_member'] + fields
        else:
            fields = ['member'] + fields

        return fields

    def get_readonly_fields(self, request, obj=None):
        """
        En caso de estar editando una compra, no permitir modificar el
        estudiante.
        """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(SpecialPurchaseAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields + ['_link_member']

        if obj:
            fields += ['_link_member', 'product']

            if obj.reported_in is not None:
                fields += ['date_created', 'quantity', 'amount', 'concept', 'billable']
        else:
            fields += ['date_created']

        return fields

    def get_student_id(self, obj: SpecialPurchase):
        return obj.member.student_id

    get_student_id.short_description = _('id')

    def _total(self, obj: SpecialPurchase):
        return pretty_currency(obj.quantity * obj.amount)

    _total.short_description = 'Total'

    def has_delete_permission(self, request, obj=None):
        """
        Si todavia no fue reportada permitir que se borre la compra.
        """
        if obj is None or obj.reported_in is not None:
            return False

        return True

    def _link_member(self, obj: SpecialPurchase):
        return mark_safe('<a href="%s">%s</a>' % (reverse('admin:facturacion_student_change', args=[obj.member.id]),
                                                  obj.member.name))

    _link_member.short_description = 'miembro'

import logging
from locale import currency as pretty_currency

from django.db.models import F, DecimalField, ExpressionWrapper, Sum
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from contrib import MemberSearchWidget, CustomModelAdmin, CustomTabularInline
from facturacion import models

logger = logging.getLogger(__name__)


class PurchaseItemInline(CustomTabularInline):
    model = models.CashPurchaseItem

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = models.Product.active.order_by('name')
        return super(PurchaseItemInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_extra(self, request, obj=None, **kwargs):

        if obj is None:
            return 1

        return 0

    def get_readonly_fields(self, request, obj=None):
        fields = super(PurchaseItemInline, self).get_readonly_fields(request, obj)

        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['product', 'quantity']

        return fields


class PurchaseForm(ModelForm):
    class Meta:
        model = models.CashPurchase
        fields = ['student', 'date_created']
        widgets = {
            'student': MemberSearchWidget,
        }


class CashPurchaseAdmin(CustomModelAdmin):
    inlines = [PurchaseItemInline]
    ordering = ['-date_created']
    search_fields = ['student__name', 'student__student_id']
    form = PurchaseForm
    date_hierarchy = 'date_created'
    list_filter = ['cashpurchaseitem__product']

    def get_list_display(self, request):
        """
        Solo mostramos si fue reportado o no al administrador
        """
        ans = ['get_student_id', 'student', 'total', 'date_created']

        return ans

    def get_list_display_links(self, request, list_display):
        """
        Mostrar el nombre y el legajo como links en la lista
        """
        return ['get_student_id', 'student']

    def get_fields(self, request, obj=None):
        """
        Si estamos modificando un estudiante, mostrar un link a su pagina.
        """

        if obj:
            ans = ['link_student']
        else:
            ans = ['student']

        return ans + ['date_created']

    def get_readonly_fields(self, request, obj=None):
        """
        En caso de estar editando una compra, no permitir modificar el
        estudiante.
        """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(CashPurchaseAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields + ['link_student']

        if obj:
            fields += ['link_student']

        else:
            fields += ['date_created']

        return fields

    def get_student_id(self, obj):
        return obj.student.student_id

    get_student_id.short_description = _('id')

    def get_queryset(self, request):
        """
        Agregamos los purchaseitems para calcular el total de la compra. Ahorra querys
        para no preguntar compra por compra cuanto costo.
        """
        qs = super(CashPurchaseAdmin, self).get_queryset(request).annotate(
            total=ExpressionWrapper(Sum(F('cashpurchaseitem__product__price') * F('cashpurchaseitem__quantity')),
                                    output_field=DecimalField(max_digits=8, decimal_places=2))
        )

        return qs

    def total(self, obj):
        return pretty_currency(obj.total)

    def has_delete_permission(self, request, obj=None):
        return True

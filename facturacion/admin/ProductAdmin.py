import logging
from locale import currency as pretty_currency

from django.contrib import messages
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin, CustomTabularInline
from contrib.listfilters import ActiveListFilter
from informacion.models import InventoryEntry

logger = logging.getLogger(__name__)


class InventoryEntryInline(CustomTabularInline):
    model = InventoryEntry
    extra = 0
    # fields = ['service']
    readonly_fields = ['name', 'date_created', 'description', 'location', 'quantity']
    fields = ['name', 'date_created', 'description', 'location', 'quantity']
    show_change_link = True

    def get_queryset(self, request):
        return super(InventoryEntryInline, self).get_queryset(request).order_by('date_created')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(InventoryEntryInline, self).get_readonly_fields(request=request, obj=obj)
        if fields:
            return fields

        return fields


class ProductAdmin(CustomModelAdmin):
    list_display = ['name', 'price_with_dollar', 'date_created', '_inventory', 'minimum_stock', 'is_active']
    list_filter = [ActiveListFilter]
    ordering = ['name']
    inlines = [InventoryEntryInline]

    def price_with_dollar(self, obj):
        return pretty_currency(obj.price)

    price_with_dollar.short_description = _("price")

    def get_fields(self, request, obj=None):
        """
        Permitir ver la fecha de alta y baja de un producto.
        """
        ans = ['name', 'price', 'track_inventory', 'minimum_stock']

        if obj:
            ans += ['date_created', 'date_removed']

        return ans

    def get_readonly_fields(self, request, obj=None):
        """
         Si el usuario es superuser permitirle modificar las fechas de creacion
         y de baja
         """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(ProductAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if not request.user.is_superuser:
            return fields + ['date_created', 'date_removed', 'track_inventory']

        return fields

    def has_delete_permission(self, request, obj=None):
        """
        Solo permitir remover productos que se encuentren activos.
        """

        if obj is None:
            return False

        return obj.is_active()

    def save_model(self, request, obj, form, change):
        """
        Al guardar el producto, verificar que no exista uno ya activado.
        En caso de que exista, desactivarlo y crear este.
        """

        if obj.save():
            messages.add_message(request, messages.WARNING, _(
                "A product with this name already existed. It was disabled to use the one just created."))
            logger.info("Reemplazado producto ya existente por %s", obj)

    def get_queryset(self, request):
        """
        Agregamos los purchaseitems para calcular el total de la compra. Ahorra querys
        para no preguntar compra por compra cuanto costo.
        """
        qs = super(ProductAdmin, self).get_queryset(request).annotate(ann_inventory=Sum('inventoryentry__quantity'))

        return qs

    def _inventory(self, obj):
        return obj.ann_inventory

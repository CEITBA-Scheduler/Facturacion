import logging
from locale import currency as pretty_currency

from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin

logger = logging.getLogger(__name__)


class JournalEntryAdmin(CustomModelAdmin):
    list_display = ['id', 'who', '_truncated_description', '_amount_in', '_amount_out', 'date_paid', 'date_created']
    ordering = ['-id']
    search_fields = ['description', 'who']

    def get_fieldsets(self, request, obj=None):
        if obj:

            initial = [
                (
                    None, {
                        'fields': ('_id', 'who', 'description')
                    }
                )
            ]

            if obj.amount_out:
                initial += [
                    (
                        "Egresos", {
                            'fields': ('_amount_out', 'date_created')
                        }
                    )
                ]
            if obj.amount_in:
                initial += [
                    (
                        "Ingresos", {
                            'fields': ('_amount_in', "date_paid"),
                        }
                    )
                ]

            return initial
        else:
            return (
                (
                    None, {
                        'fields': ('who', 'description')
                    }
                ),
                (
                    "Egresos", {
                        'fields': ('amount_out', 'date_created')
                    }
                ),
                (
                    "Ingresos", {
                        'fields': ('amount_in', "date_paid"),
                    }
                )
            )

    def _amount_in(self, obj):
        return pretty_currency(obj.amount_in, grouping=True) if obj.amount_in else "-"

    _amount_in.short_description = 'ingresos'

    def _amount_out(self, obj):
        return pretty_currency(obj.amount_out, grouping=True) if obj.amount_out else "-"

    _amount_out.short_description = 'egresos'

    def _id(self, obj):
        return obj.id

    _id.short_description = _('ID')

    def get_readonly_fields(self, request, obj=None):
        """
        En caso de que ya se haya creado, no permitir el cambio de nombre
        """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(JournalEntryAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            # FIXME: Ver 505
            return ['_id', 'who', 'description', 'date_created', 'date_paid', '_amount_in', '_amount_out']

        return ['_amount_in', '_amount_out', '_id']

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def _truncated_description(self, obj):
        """
        Trunca el concepto del reembolso a 40 caracteres para ser mostrado en la lista.
        """
        return truncatechars(obj.description, 40)

    _truncated_description.short_description = _('description')

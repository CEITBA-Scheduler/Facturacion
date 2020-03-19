import logging
from locale import currency as pretty_currency

from django.forms import ModelForm
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin, MemberSearchWidget
from facturacion.models import Reimbursement

logger = logging.getLogger(__name__)


class ReimbursementForm(ModelForm):
    class Meta:
        model = Reimbursement
        fields = ['student', 'concept', 'amount']
        widgets = {
            'student': MemberSearchWidget,
        }


class ReimbursementAdmin(CustomModelAdmin):
    # raw_id_fields = ['student']
    search_fields = ['student__name', 'student__student_id']
    ordering = ['-date_created']
    form = ReimbursementForm

    def get_list_display(self, request):
        """
        Solo mostramos si fue reportado o no al administrador
        """
        ans = ['get_student_id', 'student', 'amount_with_dollar', 'date_created', '_truncated_concept']

        if request.user.is_superuser:
            ans += ['is_reported']

        return ans

    def get_list_display_links(self, request, list_display):
        return ['get_student_id', 'student']

    def get_fields(self, request, obj=None):
        """
        Si estamos modificando un reembolso, mostrar un link a su pagina.
        """

        if obj:
            ans = ['link_student']
        else:
            ans = ['student']

        return ans + ['concept', 'amount']

    def get_readonly_fields(self, request, obj=None):
        """
        En caso de que ya se haya reportado, no permitir la modificacion del concepto o monto.
        """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(ReimbursementAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['link_student']

            if obj.reported_in is not None:
                fields += ['concept', 'amount']

        return fields

    def get_student_id(self, obj):
        return obj.student.student_id

    get_student_id.short_description = _('id')

    def amount_with_dollar(self, obj):
        return pretty_currency(obj.amount, grouping=True)

    amount_with_dollar.short_description = _("amount")

    def _truncated_concept(self, obj):
        """
        Trunca el concepto del reembolso a 40 caracteres para ser mostrado en la lista.
        """
        return truncatechars(obj.concept, 40)

    _truncated_concept.short_description = _("concept")

    def has_delete_permission(self, request, obj=None):
        """
        Solo permitir borrar el reembolso si todavia no fue reportado en una facturacion.
        """
        if obj is None or obj.reported_in is not None:
            return False

        return True

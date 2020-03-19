from locale import currency as pretty_currency

from django.forms import ModelForm

from contrib import CustomModelAdmin, MemberSearchWidget
from informacion.models import AlquilerMate


class AlquilerMateForm(ModelForm):
    class Meta:
        model = AlquilerMate
        fields = ['member', 'kit_number', 'amount_donated', 'time_taken', 'time_returned']
        widgets = {
            'member': MemberSearchWidget,
        }


class AlquilerMateAdmin(CustomModelAdmin):
    list_display = ['member', 'kit_number', 'time_taken', 'time_returned', '_amount_donated']
    search_fields = ['member__name', 'member__student_id']
    fields = ['member', 'kit_number', 'amount_donated', 'time_taken', 'time_returned', 'paid_in_cash']

    form = AlquilerMateForm

    def get_readonly_fields(self, request, obj=None):
        fields = super(AlquilerMateAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if request.user.is_superuser:
            return []

        if obj:
            fields += ['member', 'kit_number', 'time_taken', 'paid_in_cash']

            if obj.time_returned:
                fields += ['amount_donated', 'time_returned']

        if not obj:
            fields += ['time_taken', 'time_returned']

        return fields

    def _amount_donated(self, obj: AlquilerMate):
        return pretty_currency(obj.amount_donated, grouping=True)

    _amount_donated.short_description = 'Monto donado'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

from django.forms import ModelForm

from contrib import CustomModelAdmin, MemberSearchWidget
from informacion.models import Lend


class LendForm(ModelForm):
    class Meta:
        model = Lend
        fields = ['member', 'time_taken', 'time_returned', 'lended_object']
        widgets = {
            'member': MemberSearchWidget,
        }


class LendAdmin(CustomModelAdmin):
    list_display = ['_student_id', 'member', 'time_taken', 'time_returned']
    search_fields = ['member__name', 'member__student_id']
    fields = ['member', 'time_taken', 'time_returned', 'lended_object']
    list_display_links = ['_student_id', 'member']

    form = LendForm

    def get_readonly_fields(self, request, obj=None):
        fields = super(LendAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if request.user.is_superuser:
            return []

        if obj:
            fields += ['member', 'time_taken', 'lended_object']

            if obj.time_returned:
                fields += ['time_returned']

        if not obj:
            fields += ['time_taken', 'time_returned']

        return fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def _student_id(self, obj: Lend):
        return obj.member.student_id

    _student_id.short_description = 'Legajo'

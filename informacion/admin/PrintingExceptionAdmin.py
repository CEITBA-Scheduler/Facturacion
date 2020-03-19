from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin, MemberSearchWidget
from informacion.models import PrintingException


class PrintingExceptionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PrintingExceptionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PrintingException
        fields = ['member', 'count', 'date']
        widgets = {
            'member': MemberSearchWidget,
        }


class PrintingExceptionAdmin(CustomModelAdmin):
    list_display = ['_student_id', '_student_name', 'date', 'count']
    fields = ['member', 'count', 'date']
    readonly_fields = ['date']
    form = PrintingExceptionForm

    def get_readonly_fields(self, request, obj=None):
        fields = super(PrintingExceptionAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        return fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def _student_id(self, obj):
        return obj.member.student_id

    _student_id.short_description = _('id')

    def _student_name(self, obj):
        return obj.member.name

    _student_name.short_description = _('name')

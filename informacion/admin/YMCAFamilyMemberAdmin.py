from constance import config
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from contrib import CustomModelAdmin
from facturacion.models import Enrollment
from informacion.models import YMCAFamilyMember


class YMCAEnrollmentSearchWidget(ModelSelect2Widget):
    """
    Widget para poder buscar enrollments por nombre o legajo sin tener que abrir una ventana
    aparte.
    """

    search_fields = [
        'student__name__icontains', 'student__student_id__icontains'
    ]

    def build_attrs(self, base_attrs, extra_attrs=None, **kwargs):
        attrs = super(YMCAEnrollmentSearchWidget, self).build_attrs(base_attrs, extra_attrs=extra_attrs, **kwargs)

        attrs['style'] = "width: 300px"
        attrs['data-placeholder'] = _("search a student by name or id")

        return attrs

    def get_queryset(self):
        return Enrollment.active.filter(
            service__name=config.YMCA_SERVICE_NAME
        )


class YMCAFamilyMemberForm(ModelForm):
    class Meta:
        model = YMCAFamilyMember
        fields = ['enrollment', 'family_members']
        widgets = {
            'enrollment': YMCAEnrollmentSearchWidget,
        }


class YMCAFamilyMemberAdmin(CustomModelAdmin):
    list_display = ['id', '_member_id', '_member_name']
    search_fields = ['enrollment__student__name', 'enrollment__student__student_id']
    fields = ['enrollment', 'family_members']
    list_display_links = ['_member_id', '_member_name']
    form = YMCAFamilyMemberForm

    def get_readonly_fields(self, request, obj=None):

        fields = super(YMCAFamilyMemberAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj is not None:
            fields += ['enrollment']

        return fields

    def _member_id(self, obj):
        return obj.enrollment.student.student_id

    _member_id.short_description = _('id')

    def _member_name(self, obj):
        return obj.enrollment.student.name

    _member_name.short_description = _('member')

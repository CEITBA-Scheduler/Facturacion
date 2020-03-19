from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin, EnrollmentSearchWidget
from lockers.models import LockerAssignation


class LockerAssignationForm(ModelForm):
    class Meta:
        model = LockerAssignation
        fields = ['enrollment', 'locker_id']
        widgets = {
            'enrollment': EnrollmentSearchWidget,
        }


class LockerAssignationAdmin(CustomModelAdmin):
    fields = ['enrollment', 'locker_id']
    list_display = ['_member_id', '_member_name', '_lockersite', 'locker_id']
    form = LockerAssignationForm
    search_fields = ['enrollment__student__name', 'enrollment__student__student_id']
    list_filter = ['enrollment__service__lockersite']
    list_display_links = ['_member_id', '_member_name']
    ordering = ['enrollment__service__lockersite', 'locker_id']

    def _lockersite(self, obj):
        return obj.enrollment.service.lockersite

    _lockersite.short_description = _('Locker Site')

    def get_queryset(self, request):
        qs = super(LockerAssignationAdmin, self).get_queryset(request)

        return qs.select_related('enrollment', 'enrollment__service', 'enrollment__service__lockersite',
                                 'enrollment__student')

    def _member_id(self, obj):
        return obj.enrollment.student.student_id

    _member_id.short_description = _('id')

    def _member_name(self, obj):
        return obj.enrollment.student.name

    _member_name.short_description = _('member')

    def get_readonly_fields(self, request, obj=None):

        fields = super(LockerAssignationAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj is not None:
            fields += ['enrollment']

        # FIXME: Solo permitir al admin
        if not request.user.is_superuser and obj is not None:
            fields += ['locker_id']

        return fields

from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin, MemberSearchWidget
from lockers.models import LockerQueue, LockerHold


class LockerQueueForm(ModelForm):
    # send_email = forms.BooleanField(
    #     required=False,
    #     label=_("Send Email"),
    #     help_text=_("Select this to send an email notification to user."),
    #     initial=False
    # )
    #
    # auto_assign = forms.BooleanField(
    #     required=False,
    #     label=_("Auto assign"),
    #     help_text=_("Select this to automatically assign a locker if it's available."),
    #     initial=True
    # )

    class Meta:
        model = LockerQueue
        fields = ['locker_site', 'member']
        widgets = {
            'member': MemberSearchWidget,
        }


class LockerQueueAdmin(CustomModelAdmin):
    list_display = ['_member_id', '_member_name', 'locker_site', 'date_created', '_on_hold']
    fields = ['locker_site', 'member']
    list_display_links = ['_member_id', '_member_name']
    list_filter = ['locker_site']
    search_fields = ['member__name', 'member__student_id']
    form = LockerQueueForm
    ordering = ['date_created']

    def _member_id(self, obj):
        return obj.member.student_id

    _member_id.short_description = _('id')

    def _member_name(self, obj):
        return obj.member.name

    _member_name.short_description = _('member')

    # def get_queryset(self, request):
    #     qs = super(LockerQueueAdmin, self).get_queryset(request)
    #
    #     return qs.select_related('student')

    def get_readonly_fields(self, request, obj=None):
        fields = super(LockerQueueAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['locker_site', 'member']

        return fields

    def _on_hold(self, obj: LockerQueue):
        return LockerHold.objects.filter(member=obj.member, locker_site=obj.locker_site).exists()

    _on_hold.boolean = True
    _on_hold.short_description = _('On Hold')

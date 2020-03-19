import logging

from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin, MemberSearchWidget
from lockers.models import LockerHold

logger = logging.getLogger(__name__)


class LockerHoldForm(ModelForm):
    class Meta:
        model = LockerHold
        fields = ['locker_site', 'locker_id']
        widgets = {
            'member': MemberSearchWidget,
        }


class LockerHoldAdmin(CustomModelAdmin):
    list_display = ['_member_id', '_member_name', 'locker_site', 'locker_id', 'date_created']
    fields = ['locker_site', 'locker_id', 'member']
    list_display_links = ['_member_id', '_member_name']
    list_filter = ['locker_site']
    search_fields = ['member__name', 'member__student_id']
    form = LockerHoldForm
    ordering = ['locker_site', 'locker_id']

    def _member_id(self, obj: LockerHold):
        return obj.member.student_id

    _member_id.short_description = _('id')

    def _member_name(self, obj: LockerHold):
        return obj.member.name

    _member_name.short_description = _('member')

    def _locker_site(self, obj: LockerHold):
        return obj.locker_site

    _locker_site.short_description = _('locker site')

    # def get_queryset(self, request):
    #     qs = super(LockerQueueAdmin, self).get_queryset(request)
    #
    #     return qs.select_related('student')

    def get_readonly_fields(self, request, obj: LockerHold = None):
        fields = super(LockerHoldAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['locker_site', 'locker_id', 'member']

        return fields

        # def save_model(self, request, obj: LockerHold, form, change):
        #     obj.save()

        # if obj.new_assignation is not None:
        #     messages.success(request,
        #                      'Se ha encontrado un locker para el alumno, aqui puede ver el número asignado.')
        #
        # else:
        #     logger.warning(request,
        #                    'Error en la asignacion de locker: %s', obj)

    def response_add(self, request, obj: LockerHold, post_url_continue="../%s/"):
        if '_continue' not in request.POST and obj.new_assignation is not None:
            return HttpResponseRedirect(
                reverse('admin:lockers_lockerassignation_change', args=(obj.new_assignation.pk,))
            )
        else:
            return super(LockerHoldAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj: LockerHold):
        if '_continue' not in request.POST and obj.new_assignation is not None:
            return HttpResponseRedirect(
                reverse('admin:lockers_lockerassignation_change', args=(obj.new_assignation.pk,))
            )
        else:
            return super(LockerHoldAdmin, self).response_change(request, obj)

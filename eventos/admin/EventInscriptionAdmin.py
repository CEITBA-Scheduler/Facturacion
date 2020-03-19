import logging

from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from eventos.models import EventInscription
from contrib import CustomModelAdmin, MemberSearchWidget

logger = logging.getLogger(__name__)


class EventInscriptionForm(ModelForm):
    class Meta:
        model = EventInscription
        fields = ['event', 'member']
        widgets = {
            'member': MemberSearchWidget,
        }


class EventInscriptionAdmin(CustomModelAdmin):
    list_display = ['id', 'event', 'member', 'date_created', 'extra_info']
    list_display_links = ['id', 'event', 'member']
    ordering = ['date_created']
    form = EventInscriptionForm

    def get_readonly_fields(self, request, obj=None):
        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(EventInscriptionAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['event', '_link_member']

        return fields

    def get_fields(self, request, obj=None):
        fields = ['event']

        if obj is not None:
            fields += ['_link_member']
        else:
            fields += ['member']

        return fields + ['extra_info']

    def _link_member(self, obj):
        return mark_safe(
            '<a href="%s">%s</a>' % (reverse('admin:facturacion_student_change', args=[obj.member.id]),
                                     obj.member.name))

    _link_member.short_description = 'Miembro'

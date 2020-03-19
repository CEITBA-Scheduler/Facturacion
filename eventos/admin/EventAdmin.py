import logging

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from contrib import CustomTabularInline, CustomModelAdmin
from eventos.models import EventInscription

logger = logging.getLogger(__name__)


class EventInscriptionInline(CustomTabularInline):
    model = EventInscription
    extra = 0
    fields = ['member', 'date_created']
    readonly_fields = ['member', 'date_created']
    # fields = ['is_active', 'service', 'date_created', 'date_removed']
    show_change_link = True

    def get_queryset(self, request):
        return super(EventInscriptionInline, self).get_queryset(request).order_by('date_created')

    def has_add_permission(self, request):
        return False


class EventAdmin(CustomModelAdmin):
    list_display = ['name', 'max_participants', 'date_created', 'inscription_end', '_export_link']
    fields = ['name', 'max_participants', 'inscription_end']
    ordering = ['date_created']
    inlines = [EventInscriptionInline]

    def get_readonly_fields(self, request, obj=None):
        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(EventAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['name']

        return fields

    def _export_link(self, obj):
        return mark_safe(
            '<a href="%s?event=%s">%s</a>' % (
                reverse('admin:export_event'),
                obj.pk,
                _('Export to Excel')
            )
        )

    _export_link.short_description = _('Export')

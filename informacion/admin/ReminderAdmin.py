import logging

from django.template.defaultfilters import truncatechars

from contrib import CustomModelAdmin

logger = logging.getLogger(__name__)


class ReminderAdmin(CustomModelAdmin):
    list_display = ['id', '_content', 'completed']
    fields = ['content', 'completed']
    list_display_links = ['id', '_content']
    list_filter = ['completed']
    allow_delete_action = True

    def _content(self, obj):
        return truncatechars(obj.content, 40)

    _content.short_description = 'contenido'

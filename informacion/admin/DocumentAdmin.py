import logging

from contrib import CustomModelAdmin

logger = logging.getLogger(__name__)


class DocumentAdmin(CustomModelAdmin):
    list_display = ['id', 'title', 'document']
    fields = ['title', 'document']
    list_display_links = ['id', 'title']
    allow_delete_action = True

    def get_readonly_fields(self, request, obj=None):
        fields = super(DocumentAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['document']

        return fields

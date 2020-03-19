import logging

from contrib import CustomModelAdmin
from informacion.models import MediaObject

logger = logging.getLogger(__name__)


class MediaObjectAdmin(CustomModelAdmin):
    list_display = ['id', 'media_file', 'screen_time', 'published_tv', 'published_web', 'published_apuntes']
    fields = ['media_file', 'screen_time', 'published_tv', 'published_web', 'published_apuntes']
    list_display_links = ['id', 'media_file']
    list_filter = ['published_tv', 'published_web', 'published_apuntes']
    allow_delete_action = True

    def get_readonly_fields(self, request, obj=None):
        fields = super(MediaObjectAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['media_file']

        return fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj: MediaObject, form, change):
        super(MediaObjectAdmin, self).save_model(request, obj, form, change)
        logger.info("Archivo %s guardado por %s. change=%s, published=%s", obj, request.user, change, obj.published_tv)

    def delete_model(self, request, obj):
        logger.info("Archivo %s eliminado por %s.", obj, request.user)
        super(MediaObjectAdmin, self).delete_model(request, obj)

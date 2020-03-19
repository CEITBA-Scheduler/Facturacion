from datetime import date

from django.core.cache import cache

from bar.models import MenuDescription
from bar.views import MENU_V1_CACHE_KEY
from contrib import CustomModelAdmin


class MenuDescriptionAdmin(CustomModelAdmin):
    list_display = ['menu', 'for_date', 'description', '_editable']
    fields = ['menu', 'for_date', 'description']
    list_filter = ['menu']
    ordering = ['-for_date']

    def get_readonly_fields(self, request, obj: MenuDescription = None):
        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(MenuDescriptionAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if not request.user.is_superuser and obj and obj.for_date < date.today():
            return fields + ['menu', 'for_date', 'description']

        return fields

    def _editable(self, obj: MenuDescription):
        return obj.for_date >= date.today()

    def has_delete_permission(self, request, obj=None):
        return obj and self._editable(obj)

    _editable.short_description = 'editable'
    _editable.boolean = True

    def save_model(self, *args, **kwargs):
        super(MenuDescriptionAdmin, self).save_model(*args, **kwargs)

        cache.delete(MENU_V1_CACHE_KEY)

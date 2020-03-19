from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin


class PrinterCountAdmin(CustomModelAdmin):
    list_display = ['_get_student_id', 'member', 'print_count']
    fields = ['member', 'print_count', 'last_updated']
    list_display_links = ['_get_student_id', 'member']
    search_fields = ['member__name', 'member__student_id']
    ordering = ['-print_count']

    def get_readonly_fields(self, request, obj=None):

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(PrinterCountAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        fields += ['member', 'last_updated']

        if not request.user.is_superuser:
            fields += ['member', 'last_updated']

        return fields

    def _get_student_id(self, obj):
        return obj.member.student_id

    _get_student_id.short_description = _('id')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

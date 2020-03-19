from contrib import CustomModelAdmin


class PrinterReportAdmin(CustomModelAdmin):
    list_display = ['id', 'date_uploaded']
    fields = ['date_uploaded', 'file']
    list_display_links = ['id', 'date_uploaded']
    date_hierarchy = 'date_uploaded'

    def get_readonly_fields(self, request, obj=None):
        fields = super(PrinterReportAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            return fields + ['file', 'date_uploaded']

        return fields + ['date_uploaded']

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

from contrib import CustomModelAdmin


class InventoryLocationAdmin(CustomModelAdmin):
    list_display = ['id', 'location']
    fields = ['location']
    search_fields = ['location']

    def get_readonly_fields(self, request, obj=None):
        fields = super(InventoryLocationAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        return fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

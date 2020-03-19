from contrib import CustomModelAdmin


class InventoryCategoryAdmin(CustomModelAdmin):
    list_display = ['id', 'name']
    fields = ['name']
    search_fields = ['name']

    def get_readonly_fields(self, request, obj=None):
        fields = super(InventoryCategoryAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        return fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

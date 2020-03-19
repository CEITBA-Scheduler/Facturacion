from django.forms import ModelForm

from contrib import CustomModelAdmin, MemberSearchWidget
from informacion.models import SportCertificate


class SportCertificateForm(ModelForm):
    class Meta:
        model = SportCertificate
        fields = ['member', 'certificate', 'date_emitted']
        widgets = {
            'member': MemberSearchWidget,
        }


class SportCertificateAdmin(CustomModelAdmin):
    list_display = ['member', 'date_emitted', '_expiration_date']
    fields = ['member', 'certificate', 'date_emitted']
    search_fields = ['member__name', 'member__student_id']
    form = SportCertificateForm

    def get_readonly_fields(self, request, obj=None):
        fields = super(SportCertificateAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj and not request.user.is_superuser:
            fields += ['member', 'certificate', 'date_emitted']

        return fields

    def _expiration_date(self, obj):
        return obj.expiration_date

    _expiration_date.short_description = 'fecha de expiración'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

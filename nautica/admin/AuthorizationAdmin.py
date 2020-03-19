from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin, MemberSearchWidget
from nautica.fields import DNIField
from nautica.models import Authorization


class AuthorizationForm(ModelForm):
    dni = DNIField(
        label='DNI'
    )

    class Meta:
        model = Authorization
        fields = ['member', 'dni', 'auth_type']
        widgets = {
            'member': MemberSearchWidget,
        }


class AuthorizationAdmin(CustomModelAdmin):
    list_display = ['_member_id', '_member_name', 'dni', 'auth_type']
    fields = ['member', 'dni', 'auth_type']
    list_display_links = ['_member_id', '_member_name']
    list_filter = ['auth_type']
    search_fields = ['member__name', 'member__student_id', 'dni']
    form = AuthorizationForm

    def get_readonly_fields(self, request, obj=None):
        fields = super(AuthorizationAdmin, self).get_readonly_fields(request=request, obj=obj)
        if fields:
            return fields

        ans = []

        if obj:
            ans += ['member', 'dni', 'auth_type']

        return ans

    def _member_id(self, obj):
        return obj.member.student_id

    _member_id.short_description = _('id')

    def _member_name(self, obj):
        return obj.member.name

    _member_name.short_description = _('member')

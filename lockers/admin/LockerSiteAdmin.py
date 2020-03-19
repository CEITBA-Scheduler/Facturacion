from django.forms import ModelForm
from django.urls import reverse
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from contrib import CustomModelAdmin
from facturacion.models import Service
from lockers.models import LockerSite


class LockerSiteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(LockerSiteForm, self).__init__(*args, **kwargs)
        if 'service' in self.fields:
            lockersites = LockerSite.objects.all()

            self.fields['service'].queryset = Service.objects.filter(type=Service.LOCKER).exclude(
                lockersite__in=lockersites)

    class Meta:
        model = LockerSite
        fields = ['service', 'count']


class LockerSiteAdmin(CustomModelAdmin):
    fields = ['service', 'count']
    list_display = ['service', 'count', '_used', '_free', '_export_link']  # , '_next_free_locker']
    form = LockerSiteForm

    def has_delete_permission(self, request, obj=None):
        """
        No permitir borrar las categorias
        """
        return False

    def _used(self, obj):
        return '%d' % obj.used_spots()

    _used.short_description = _('used')

    def _free(self, obj):
        return '%d' % obj.free_spots()

    _free.short_description = _('free')

    def _next_free_locker(self, obj):
        return '%d' % obj.get_free_locker() if not None else '-'

    _next_free_locker.short_description = _('next free locker')

    # def get_fields(self, request, obj=None):
    #     ans = []
    #
    #     if not obj:
    #         ans += ['service']
    #
    #     return ans + ['count']
    #

    def get_readonly_fields(self, request, obj=None):
        fields = super(LockerSiteAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['service']

        return fields

    def _export_link(self, obj):
        return mark_safe(
            '<a href="%s?lockersite=%s">%s</a>' % (
                reverse('admin:export_lockersite'),
                urlquote(obj.pk),
                _('Export to Excel')
            )
        )

    _export_link.short_description = _('Export')

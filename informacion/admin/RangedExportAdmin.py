import logging

from django.forms import ModelForm

from contrib import CustomModelAdmin
from facturacion.models import Service
from informacion.models import RangedExport

logger = logging.getLogger(__name__)


class RangeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RangeForm, self).__init__(*args, **kwargs)
        if 'service' in self.fields:
            self.fields['service'].queryset = Service.active.all()

    class Meta:
        model = RangedExport
        fields = ['service', 'start_date', 'end_date', 'exported_file']


class RangedExportAdmin(CustomModelAdmin):
    list_display = ['id', 'service', 'start_date', 'end_date']
    list_display_links = ['id', 'service']
    form = RangeForm

    def get_fields(self, request, obj=None):
        """
        Si estamos modificando un enrollment mostramos un link al estudiante. Si es nuevo permitimos
        al usuario que seleccine un estudiante por id. Mostramos el servicio al que esta asociado.
        Si es un enrollment nuevo permitimos facturar el examen medico automaticamente, caso contrario
        mostramos la fecha de alta y de baja.
        """
        if obj is None:
            ans = ['service', 'start_date', 'end_date']
        else:
            ans = ['service', 'start_date', 'end_date', 'exported_file']

        return ans

    def get_readonly_fields(self, request, obj=None):
        """
        Si estamos modificando un enrollment existente, mostramos un link a la pagina del estudiante
        y el servicio al que se dio de alta.
        Si el usuario activo es el administrador mostramos la fecha de alta y de baja.
        """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(RangedExportAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['service', 'start_date', 'end_date', 'exported_file']

        return fields

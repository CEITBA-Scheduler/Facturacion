import datetime
import logging
from locale import currency as pretty_currency

from django.db.models.functions import Greatest, Coalesce
from django.forms import ModelForm, BooleanField
from django.utils.translation import ugettext_lazy as _

from contrib import CustomTabularInline, MemberSearchWidget, CustomModelAdmin
from contrib.listfilters import ActiveListFilter, ActiveServiceListFilter
from facturacion.models import Enrollment, Service

logger = logging.getLogger(__name__)


class EnrollmentInline(CustomTabularInline):
    model = Enrollment
    extra = 0
    # fields = ['service']
    readonly_fields = ['service', 'date_created', 'date_removed']
    fields = ['is_active', 'service', 'date_created', 'date_removed']
    show_change_link = True

    def get_queryset(self, request):
        return super(EnrollmentInline, self).get_queryset(request).order_by('date_removed')

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(EnrollmentInline, self).get_readonly_fields(request=request, obj=obj)
        if fields:
            return fields + ['is_active']


class EnrollmentForm(ModelForm):
    """
    Campo para permitir facturar automaticamente el examen medico de YMCA sin tener que crear una
    compra al finalizar el agregado de la suscripcion.
    """
    add_ymca_medical_exam = BooleanField(
        required=False,
        label=_("Debit medical exam"),
        help_text=_("Select this to automatically add a purchase for the YMCA medical exam")
    )

    def __init__(self, *args, **kwargs):
        super(EnrollmentForm, self).__init__(*args, **kwargs)
        if 'service' in self.fields:
            self.fields['service'].queryset = Service.active.all()

    class Meta:
        model = Enrollment
        fields = ['student', 'service', 'billable', 'add_ymca_medical_exam']
        widgets = {
            'student': MemberSearchWidget,
        }

    class Media:
        js = ('enrollment-ymca-autohide.js',)

    def save(self, commit=True):
        instance = super(EnrollmentForm, self).save(commit=False)

        if instance.id is None:
            instance.save(add_ymca_medical_exam=self.cleaned_data['add_ymca_medical_exam'])
        else:
            instance.save()

        return instance


class EnrollmentAdmin(CustomModelAdmin):
    list_filter = [ActiveServiceListFilter, ActiveListFilter, 'student__type', 'billable']
    # raw_id_fields = ['student']
    search_fields = ['student__name', 'student__student_id']
    form = EnrollmentForm
    help_messages = [
        "Si se trata de un locker, al eliminar la suscripción se eliminará la asignación."
    ]

    # ordering = ['-date_created']

    def get_list_display(self, request):
        """
        Solo mostramos si fue reportado o no al administrador
        """
        ans = ['get_student_id', 'student', 'service', 'service_price', '_last_modified', 'is_active']

        if request.user.is_superuser:
            ans += ['is_reported']

        return ans + ['billable']

    def get_list_display_links(self, request, list_display):
        return ['get_student_id', 'student']

    def get_fields(self, request, obj=None):
        """
        Si estamos modificando un enrollment mostramos un link al estudiante. Si es nuevo permitimos
        al usuario que seleccine un estudiante por id. Mostramos el servicio al que esta asociado.
        Si es un enrollment nuevo permitimos facturar el examen medico automaticamente, caso contrario
        mostramos la fecha de alta y de baja.
        """
        if obj is None:
            ans = ['student', 'service', 'billable', 'add_ymca_medical_exam']
        else:
            ans = ['link_student', 'service', 'billable', 'date_created', 'date_removed']

        return ans

    def get_readonly_fields(self, request, obj=None):
        """
        Si estamos modificando un enrollment existente, mostramos un link a la pagina del estudiante
        y el servicio al que se dio de alta.
        Si el usuario activo es el administrador mostramos la fecha de alta y de baja.
        """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(EnrollmentAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields + ['link_student']

        if obj is not None:
            fields += ['link_student', 'service']

        if not request.user.is_superuser:
            fields += ['date_created', 'date_removed']

        return fields

    def get_student_id(self, obj):
        return obj.student.student_id

    get_student_id.short_description = _('id')

    def has_delete_permission(self, request, obj=None):
        """
        Solo dejamos que borre elementos existentes o activos. Aquellos que no esten
        activos se los considera 'eliminados' por el sistema
        """
        if obj is None:
            return False

        return obj.is_active()

    def service_price(self, obj):
        return pretty_currency(obj.service.price)

    service_price.short_description = _('service price')

    def is_reported(self, obj):
        """
        Si no se dio de baja la suscripcion, decir si fue reportado como alta.
        Si se dio de baja la suscripcion, decir si fue reportado como baja.
        """
        if obj.date_removed is None:
            return obj.reported_in_id is not None
        else:
            return obj.reported_in2_id is not None

    def _last_modified(self, obj):
        return obj.last_modified

    _last_modified.short_description = _('last modified')

    def get_queryset(self, request):
        qs = super(EnrollmentAdmin, self).get_queryset(request)

        return qs.annotate(
            last_modified=Greatest(
                'date_created',
                Coalesce('date_removed', datetime.date(2016, 1, 1))
            )
        ).order_by('-last_modified')

    is_reported.boolean = True
    is_reported.short_description = _('reported')

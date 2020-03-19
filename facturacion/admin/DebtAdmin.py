import logging
from locale import currency as pretty_currency

from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget

from contrib import CustomModelAdmin, MemberSearchWidget
from contrib.listfilters import PaidDebtFilter
from facturacion.models import Debt, Enrollment

logger = logging.getLogger(__name__)


class EnrollmentSearchWidget(ModelSelect2MultipleWidget):
    """
    Widget para poder buscar enrollments por nombre o legajo sin tener que abrir una ventana
    aparte.
    """
    model = Enrollment

    search_fields = [
        'student__name__icontains', 'student__student_id__icontains'
    ]

    def build_attrs(self, base_attrs, extra_attrs=None, **kwargs):
        attrs = super(EnrollmentSearchWidget, self).build_attrs(base_attrs, extra_attrs=extra_attrs, **kwargs)

        attrs['style'] = "width: 300px"
        attrs['data-placeholder'] = _("search a student by name or id")

        return attrs


class DebtForm(ModelForm):
    class Meta:
        model = Debt
        fields = ['student', 'enrollments', 'date_created', 'date_paid']
        widgets = {
            'student': MemberSearchWidget,
            'enrollments': EnrollmentSearchWidget
        }


class DebtAdmin(CustomModelAdmin):
    search_fields = ['student__name', 'student__student_id']
    ordering = ['-date_created', 'student__student_id']
    list_filter = [PaidDebtFilter, 'student__type']
    form = DebtForm

    def get_list_display(self, request):

        ans = ['get_student_id', 'student', 'amount_with_dollar', 'date_created', 'date_paid', '_is_paid']

        return ans

    def get_list_display_links(self, request, list_display):
        return ['get_student_id', 'student']

    def get_fields(self, request, obj=None):
        """
        Si estamos modificando un reembolso, mostrar un link a su pagina.
        """

        if obj:
            return ['link_student', 'date_created', 'amount_with_dollar', 'date_paid', 'enrollments', 'bill']

        return ['student', 'enrollments', 'date_created', 'date_paid', 'bill']

    def get_readonly_fields(self, request, obj=None):
        """
        En caso de que ya se haya reportado, no permitir la modificacion del concepto o monto.
        """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(DebtAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if obj:
            fields += ['link_student', 'amount_with_dollar', 'date_created', 'enrollments']

            if obj.date_paid is not None and not request.user.is_superuser:
                fields += ['date_paid']

            if obj.bill:
                fields += ['bill']

        return fields

    def get_student_id(self, obj):
        return obj.student.student_id

    get_student_id.short_description = _('id')

    def amount_with_dollar(self, obj):
        return pretty_currency(obj.amount, grouping=True)

    amount_with_dollar.short_description = _("amount")

    def link_student(self, obj):
        return mark_safe(
            '<a href="%s">%s</a>' % (reverse('admin:facturacion_student_change', args=[obj.student.id]),
                                     obj.student.name))

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def _is_paid(self, obj):
        return obj.is_paid

    _is_paid.short_description = _('is paid')
    _is_paid.boolean = True

    def get_queryset(self, request):
        qs = super(DebtAdmin, self).get_queryset(request)

        return qs.select_related('student')

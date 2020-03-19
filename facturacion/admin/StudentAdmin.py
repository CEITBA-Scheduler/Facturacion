import datetime
from datetime import date

from constance import config
from django.contrib.admin import SimpleListFilter
from django.db.models import OuterRef, Exists
from django.forms import ModelForm, BooleanField
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _

from contrib import CustomTabularInline, CustomModelAdmin
from facturacion.admin.EnrollmentAdmin import EnrollmentInline
from facturacion.models import Student, Enrollment, Debt
from informacion.models import SportCertificate


class ActiveStudentListFilter(SimpleListFilter):
    title = _('active')

    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes')),
            ('0', _('No')),
        )

    def queryset(self, request, queryset):

        if self.value() == '1':
            return queryset.filter(enrollment__service__name__exact=config.CEITBA_SERVICE_NAME,
                                   enrollment__date_removed__isnull=True)
        elif self.value() == '0':
            return queryset.exclude(enrollment__service__name__exact=config.CEITBA_SERVICE_NAME,
                                    enrollment__date_removed__isnull=True)
        else:
            return queryset


class DebtsInline(CustomTabularInline):
    model = Debt
    extra = 0
    fields = ['_is_paid', 'date_created', 'enrollments', 'amount', 'date_paid', 'bill']
    readonly_fields = ['_is_paid', 'date_created', 'enrollments', 'amount']
    show_change_link = True

    def get_queryset(self, request):
        return super(DebtsInline, self).get_queryset(request).order_by('date_created')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def amount(self, obj):
        return obj.amount

    def _is_paid(self, obj):
        return obj.is_paid

    _is_paid.boolean = True
    _is_paid.short_description = _('is paid')


class SportCertificateInline(CustomTabularInline):
    model = SportCertificate
    extra = 0
    fields = ['_is_valid', 'member', 'certificate', 'date_emitted', '_expiration_date']
    readonly_fields = ['_is_valid', 'member', 'certificate', 'date_emitted', '_expiration_date']

    def get_queryset(self, request):
        return super(SportCertificateInline, self).get_queryset(request).order_by('date_uploaded')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(SportCertificateInline, self).get_readonly_fields(request=request, obj=obj)
        if fields:
            return fields

        return ['_is_valid', 'member', 'certificate', 'date_emitted']

    def _expiration_date(self, obj: SportCertificate):
        return date_format(obj.expiration_date)

    _expiration_date.short_description = 'fecha de expiración'

    def _is_valid(self, obj: SportCertificate):

        if not obj.pk:
            return False

        today = date.today()

        return (today - obj.date_emitted).days < 365

    _is_valid.boolean = True
    _is_valid.short_description = 'es valido'


class StudentForm(ModelForm):
    """
    Campo para permitir agregar o no el alumno automaticamente al CEITBA
    """
    add_ceitba_enrollment = BooleanField(
        required=False,
        label=_("Add CEITBA enrollment"),
        help_text=_("Select this to automatically add an enrollment to the CEITBA service."),
        initial=True
    )

    """
    Campo para permitir seleccionar si se factura o no
    """
    auto_bill = BooleanField(
        required=False,
        label="Facturar",
        help_text=_('Unmark if this enrollment shouldn\'t be included in a report.'),
        initial=True
    )

    class Meta:
        model = Student
        fields = ['name', 'student_id', 'email', 'dni', 'add_ceitba_enrollment', 'auto_bill']

    class Media:
        js = ('member-billable-autohide.js',)

    def save(self, commit=True):
        instance = super(StudentForm, self).save(commit=False)

        if instance.id is None:
            instance.save(
                add_ceitba_enrollment=self.cleaned_data['add_ceitba_enrollment'],
                auto_bill=self.cleaned_data['auto_bill']
            )
        else:
            instance.save()

        return instance


class StudentAdmin(CustomModelAdmin):
    list_display = ('student_id', 'name', 'email', 'dni', 'date_created', 'type', 'active')
    list_filter = [ActiveStudentListFilter, 'type']
    search_fields = ['name', 'student_id', 'dni']
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    inlines = [EnrollmentInline, SportCertificateInline, DebtsInline, AlquilerMatesInline]
=======
    inlines = [EnrollmentInline, SportCertificateInline, DebtsInline]
>>>>>>> c5b34188a09cab9d1d8a7e8c310d6ee64756161f
=======
    inlines = [EnrollmentInline, SportCertificateInline, DebtsInline]
>>>>>>> parent of 06c544f... mates en perfiles
=======
    inlines = [EnrollmentInline, SportCertificateInline, DebtsInline]
>>>>>>> parent of 053f01b... fdsa
    ordering = ['-date_created']
    list_display_links = ['name', 'student_id']
    form = StudentForm
    save_on_top = True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_fields(self, request, obj=None):
        """
        Mostramos el nombre y el legajo. En caso de estar modificando un estudiante
        tambien mostramos su fecha de creacion y de baja.
        """
        ans = ['name', 'student_id', 'email', 'dni']

        if obj:
            ans += ['date_created', 'date_removed']

        ans += ['type']

        if not obj:
            ans += ['add_ceitba_enrollment', 'auto_bill']

        return ans

    def get_readonly_fields(self, request, obj=None):
        """
        Si el usuario es superuser permitirle modificar las fechas de creacion
        y de baja
        """

        # Preguntamos si el usuario tiene permisos de guardado. Si no los tiene,
        # dejamos todos los campos en readonly
        fields = super(StudentAdmin, self).get_readonly_fields(request=request, obj=obj)
        if not self.has_save_permission(request):
            return fields

        if not request.user.is_superuser:
            fields += ['date_created', 'date_removed']

            today = date.today()
            margin = datetime.timedelta(days=config.STUDENT_ID_CHANGE_GRACE_PERIOD)

            # Si el alumno ya existe y es mas viejo que 3 dias no permitir que se modifique el legajo
            if obj is not None and (today - obj.date_created) > margin:
                fields += ['student_id']

        return fields

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Ocultamos el inline con la lista de servicios si se esta creando un estudiante
        """
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, EnrollmentInline) and ((obj is not None and not Enrollment.objects.filter(
                    student=obj
            ).exists()) or obj is None):
                continue

            if isinstance(inline, SportCertificateInline) and ((obj is not None and not SportCertificate.objects.filter(
                    member=obj
            ).exists()) or obj is None):
                continue

            if isinstance(inline, DebtsInline) and (
                    (obj is not None and not Debt.objects.filter(
                        student=obj
                    ).exists()) or obj is None):
                continue

            yield inline.get_formset(request, obj), inline

    def active(self, obj):
        return obj.ann_is_active

    def get_queryset(self, request):

        qs = super(StudentAdmin, self).get_queryset(request)

        is_active_query = Enrollment.objects.filter(
            service__name=config.CEITBA_SERVICE_NAME,
            date_removed__isnull=True,
            student__id=OuterRef('pk'),
        )

        return qs.annotate(
            ann_is_active=Exists(is_active_query)
        )

    active.boolean = True
    active.short_description = _('active')

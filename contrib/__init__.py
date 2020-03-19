import logging

from django.contrib.admin import ModelAdmin, TabularInline
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from facturacion.models import Enrollment, Service, Student
from lockers.models import LockerSite, LockerAssignation

logger = logging.getLogger('ceitba.models')


class LoggingModel(models.Model):
    class Meta:
        abstract = True

    def log_save(self, line=None):
        is_new = self.pk is None

        if is_new:
            logger.info("[%s|ADD] %s", self._meta.model_name, line or self)
        else:
            logger.info("[%s|SAVE] %s", self._meta.model_name, line or self)

    def log_delete(self):
        logger.info("[%s|DELETE] %s", self._meta.model_name, self)


class CustomModelAdmin(ModelAdmin):
    # search_placeholder = 'Nombre o Legajo'
    allow_delete_action = False
    help_messages = None

    def get_actions(self, request):
        actions = super(CustomModelAdmin, self).get_actions(request)
        if not self.allow_delete_action and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def is_reported(self, obj):
        return obj.reported_in_id is not None

    is_reported.boolean = True
    is_reported.short_description = _('reported')

    def link_student(self, obj):
        return mark_safe('<a href="%s">%s</a>' % (reverse('admin:facturacion_student_change', args=[obj.student.id]),
                                                  obj.student.name))

    link_student.short_description = _('student')

    def is_active(self, obj):
        return obj.date_removed is None

    is_active.short_description = _("active")
    is_active.boolean = True

    def has_save_permission(self, request, obj=None):
        perm = "%s.save_%s" % (self.model._meta.app_label, self.model._meta.model_name)
        return request.user.has_perm(perm)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(CustomModelAdmin, self).get_readonly_fields(request, obj=obj))

        if not self.has_save_permission(request) and obj:
            fields += [field.name for field in obj._meta.fields]

        return fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        extra_context['ceitba_can_save'] = False
        extra_context['ceitba_model'] = True
        extra_context['help_messages'] = self.help_messages

        if self.has_save_permission(request) and object_id:
            extra_context['ceitba_can_save'] = True

        return super(CustomModelAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        extra_context['help_messages'] = self.help_messages

        return super(CustomModelAdmin, self).add_view(request, form_url, extra_context=extra_context)

    def has_add_permission(self, request):
        return super(CustomModelAdmin, self).has_add_permission(request) and self.has_save_permission(request)

    def has_delete_permission(self, request, obj=None):
        return super(CustomModelAdmin, self).has_delete_permission(request, obj) and self.has_save_permission(request,
                                                                                                              obj)


class CustomTabularInline(TabularInline):
    def get_readonly_fields(self, request, obj=None):
        fields = list(super(CustomTabularInline, self).get_readonly_fields(request, obj=obj))

        if not self.has_save_permission(request) and obj:
            fields += [field.name for field in obj._meta.fields]

        return fields

    def has_save_permission(self, request, obj=None):
        perm = "%s.save_%s" % (self.model._meta.app_label, self.model._meta.model_name)
        return request.user.has_perm(perm)


class MemberSearchWidget(ModelSelect2Widget):
    """
    Widget para poder buscar estudiantes por nombre o legajo sin tener que abrir una ventana
    aparte.
    """
    search_fields = [
        'name__icontains', 'student_id__icontains'
    ]

    model = Student

    def build_attrs(self, base_attrs, extra_attrs=None, **kwargs):
        attrs = super(MemberSearchWidget, self).build_attrs(base_attrs, extra_attrs=extra_attrs, **kwargs)

        attrs['style'] = "width: 300px"
        attrs['data-placeholder'] = _("search a student by name or id")

        return attrs


class EnrollmentSearchWidget(ModelSelect2Widget):
    """
    Widget para poder buscar enrollments por nombre o legajo sin tener que abrir una ventana
    aparte.
    """

    search_fields = [
        'student__name__icontains', 'student__student_id__icontains'
    ]

    def build_attrs(self, base_attrs, extra_attrs=None, **kwargs):
        attrs = super(EnrollmentSearchWidget, self).build_attrs(base_attrs, extra_attrs=extra_attrs, **kwargs)

        attrs['style'] = "width: 300px"
        attrs['data-placeholder'] = _("search a student by name or id")

        return attrs

    def get_queryset(self):
        lockersites = LockerSite.objects.all()

        assignations = LockerAssignation.objects.all()

        return Enrollment.objects.filter(
            service__type=Service.LOCKER,
            service__lockersite__in=lockersites,
            date_removed__isnull=True
        ).exclude(lockerassignation__in=assignations)

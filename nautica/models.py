from django.db import models
from django.utils.translation import ugettext_lazy as _

from facturacion.models import Student


class Authorization(models.Model):
    member = models.ForeignKey(
        to=Student,
        verbose_name=_('member')
    )
    dni = models.CharField(
        verbose_name='DNI',
        max_length=10,
    )

    TYPE_PATRON = 'p'
    TYPE_TIMONEL = 't'

    AUTH_TYPE = (
        (TYPE_PATRON, 'Patron'),
        (TYPE_TIMONEL, 'Timonel'),
    )

    auth_type = models.CharField(
        max_length=1,
        choices=AUTH_TYPE,
        verbose_name=_('authorization type'),
        default=TYPE_TIMONEL
    )

    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=False
    )

    def __str__(self):
        return '%s' % self.member

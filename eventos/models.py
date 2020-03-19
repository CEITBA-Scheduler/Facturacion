import logging
from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _

from facturacion.models import Student

logger = logging.getLogger(__name__)


class Event(models.Model):
    name = models.CharField(
        verbose_name='nombre',
        max_length=200,
        unique=True
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today
    )
    max_participants = models.PositiveSmallIntegerField(
        verbose_name='participantes máximos',
        null=True,
        default=None,
        blank=True
    )
    inscription_end = models.DateField(
        verbose_name='fin de inscripción',
        null=True,
        default=None,
        blank=True
    )

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        permissions = (
            ('save_event', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return '%s' % self.name


class EventInscription(models.Model):
    member = models.ForeignKey(
        to=Student,
        on_delete=models.CASCADE,
        verbose_name='miembro'
    )
    event = models.ForeignKey(
        to=Event,
        on_delete=models.CASCADE,
        verbose_name='evento'
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
    )
    extra_info = models.CharField(
        verbose_name='informacion extra',
        max_length=400,
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Inscripción a Evento'
        verbose_name_plural = 'Inscripciones a Evento'
        permissions = (
            ('save_eventinscription', 'NEW: Can save changes made to the model'),
        )
        unique_together = [
            ['member', 'event']
        ]

    def __str__(self):
        return '%s a %s' % (self.member.name, self.event.name)

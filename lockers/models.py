import logging
from datetime import date

from constance import config
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from facturacion.models import Enrollment, Service, Student

logger = logging.getLogger(__name__)


class LockerSiteManager(models.Manager):
    def get_queryset(self):
        return super(LockerSiteManager, self).get_queryset().select_related('service')


class LockerSite(models.Model):
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )
    count = models.PositiveSmallIntegerField(
        verbose_name=_('count')
    )
    service = models.OneToOneField(
        Service
    )

    objects = LockerSiteManager()

    class Meta:
        verbose_name = _('Locker Site')
        verbose_name_plural = _('Locker Sites')

        permissions = (
            ('save_lockersite', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return self.service.name

    def free_spots(self):
        return self.count - self.used_spots()

    def has_free_spots(self):
        return self.free_spots() > 0

    def used_spots(self):

        used = LockerAssignation.objects.filter(
            enrollment__service__lockersite=self
        ).count()

        on_hold = LockerHold.objects.filter(
            locker_site=self
        ).count()

        return used + on_hold

    def get_free_locker(self):
        lockers = [i for i in range(1, self.count + 1)]

        used = LockerAssignation.objects.filter(enrollment__service__lockersite=self)

        for locker in used:
            lockers[locker.locker_id - 1] = None

        for i in lockers:
            if i is not None and not LockerHold.objects.filter(locker_site=self, locker_id=i).exists():
                return i

        return None


class LockerAssignation(models.Model):
    enrollment = models.OneToOneField(
        Enrollment,
        verbose_name=_('enrollment'),
        unique=True
    )
    locker_id = models.PositiveSmallIntegerField(
        verbose_name=_('locker id')
    )
    date_created = models.DateField(
        verbose_name=_('date created'),
        default=date.today,
        db_index=True
    )

    def clean(self):
        super(LockerAssignation, self).clean()

        is_new = self.pk is None

        if not is_new:
            return

        if self.locker_id > self.enrollment.service.lockersite.count:
            raise ValidationError(_('Invalid Locker ID'))

        assigned_locker = LockerAssignation.objects.filter(
            enrollment__service__lockersite=self.enrollment.service.lockersite,
            locker_id=self.locker_id
        )

        if assigned_locker.exists():
            raise ValidationError(_('This locker is already assigned'))

    class Meta:
        verbose_name = _('Locker Assignation')
        verbose_name_plural = _('Locker Assignation')

        permissions = (
            ('save_lockerassignation', 'NEW: Can save changes made to the model'),
        )

        ordering = ['locker_id']

    def __str__(self):
        return '%s #%d' % (self.enrollment, self.locker_id)

    def delete(self, delete_enrollment=True, *args, **kwargs):

        logger.info("Deleting locker assignation %s", self)

        if delete_enrollment:
            self.enrollment.delete()

        super(LockerAssignation, self).delete(*args, **kwargs)

        LockerHold.auto_hold_lockers()

    @classmethod
    def create_assignation(cls, member, lockersite, locker_id):
        new_enrollment = Enrollment()
        new_enrollment.student = member
        new_enrollment.service = lockersite.service
        new_enrollment.save()

        new_assignation = LockerAssignation()
        new_assignation.locker_id = locker_id
        new_assignation.enrollment = new_enrollment
        new_assignation.save()

        return new_assignation, new_enrollment


class LockerQueue(models.Model):
    locker_site = models.ForeignKey(
        to=LockerSite,
        verbose_name=_('locker site'),
        null=True,
        blank=True
    )
    member = models.OneToOneField(
        to=Student,
        verbose_name=_('member'),
    )
    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        default=timezone.now,
        db_index=True
    )

    class Meta:
        verbose_name = _('Locker Queue')
        verbose_name_plural = _('Locker Queue')

        ordering = ['locker_site', 'date_created']

        permissions = (
            ('save_lockerqueue', 'NEW: Can save changes made to the model'),
        )

    def clean(self):
        super(LockerQueue, self).clean()

        is_new = self.pk is None

        if not is_new:
            return

        is_in_queue = LockerQueue.objects.filter(member=self.member).exists()

        is_in_hold = LockerHold.objects.filter(member=self.member)

        has_locker = LockerAssignation.objects.filter(enrollment__student=self.member).exists()

        if is_in_queue or is_in_hold or has_locker:
            raise ValidationError(_('This member already has a locker!'))

    def save(self, *args, **kwargs):
        super(LockerQueue, self).save(*args, **kwargs)

        LockerHold.auto_hold_lockers()

    def __str__(self):
        return '%s @ %s' % (self.member, self.locker_site)


class LockerHold(models.Model):
    locker_site = models.ForeignKey(
        to=LockerSite,
        verbose_name=_('locker site'),
        null=True,
        blank=True
    )
    member = models.OneToOneField(
        to=Student,
        verbose_name=_('member'),
    )
    locker_id = models.PositiveSmallIntegerField(
        verbose_name=_('locker id')
    )
    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        default=timezone.now,
        db_index=True
    )

    class Meta:
        verbose_name = _('Locker Hold')
        verbose_name_plural = _('Locker Hold')

        ordering = ['date_created']

        permissions = (
            ('save_lockerhold', 'NEW: Can save changes made to the model'),
        )

    new_assignation = None

    def __str__(self):
        return '(%s @ %s):%s' % (self.member, self.locker_site, self.locker_id)

    def save(self, *args, **kwargs):
        logger.info("Assigning member %s to lockersite %s", self.member, self.locker_site)

        is_new = self.pk is None

        if not is_new:
            self.new_assignation, __ = LockerAssignation.create_assignation(self.member,
                                                                            self.locker_site,
                                                                            self.locker_id)

            self.delete()
            return

        if config.LOCKER_SEND_MAIL_ON_HOLD:
            logger.info("Sending notification email for new Locker Hold")

            member = self.member

            context = {
                'full_name': member.name,
            }
            subject = _('CEITBA: Tu locker ya esta disponible!')

            html_content = render_to_string('lockers/emails/locker_available.html', context)

            if member.email is not None and member.email:
                to = [member.email]
            else:

                html_content = """
                <b>El email del alumno no esta disponible!</b>
                <div>
                    %s
                </div>
                """.format(html_content)

                to = [config.CEITBA_EMAIL]

            msg = EmailMessage(
                subject=subject,
                body=html_content,
                to=to,
                reply_to=[config.CEITBA_EMAIL])
            msg.content_subtype = "html"
            try:
                msg.send()
            except Exception as e:
                logger.exception("Failed to send email. to=%s", str(to))

        super(LockerHold, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        super(LockerHold, self).delete(*args, **kwargs)

        LockerHold.auto_hold_lockers()

    def clean(self):
        super(LockerHold, self).clean()

        is_new = self.pk is None

        if not is_new:
            return

        is_reserved = LockerHold.objects.filter(
            locker_site=self.locker_site,
            locker_id=self.locker_id
        ).exists()

        is_assigned = LockerAssignation.objects.filter(
            enrollment__service__lockersite=self.locker_site,
            locker_id=self.locker_id
        ).exists()

        if is_reserved or is_assigned:
            raise ValidationError(_('This locker is already reserved!'))

    @classmethod
    def auto_hold_lockers(cls):

        if not config.LOCKER_ENABLE_AUTOHOLD:
            return

        lockersites = LockerSite.objects.all()

        for lockersite in lockersites:

            lockerqueue = LockerQueue.objects.filter(
                Q(locker_site=lockersite) | Q(locker_site__isnull=True)
            ).order_by('date_created')

            if not lockersite.has_free_spots() or not lockerqueue.exists():
                continue

            # El LockerSite tiene lugares libres y alumnos en la lista de espera

            # Mientras haya lugares libres y alumnos en la lista de espera
            while lockersite.has_free_spots() and lockerqueue.exists():
                queueitem = lockerqueue.first()

                logger.info('Creating new locker hold for %s at %s', queueitem.member, queueitem.locker_site)

                new_hold = LockerHold()
                new_hold.locker_id = lockersite.get_free_locker()
                new_hold.locker_site = lockersite
                new_hold.member = queueitem.member
                new_hold.save()  # El email se manda aca

                queueitem.delete()

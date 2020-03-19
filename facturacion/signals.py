import logging

from allauth.socialaccount.signals import pre_social_login
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from facturacion.models import Enrollment, PurchaseItem
from informacion.models import AlquilerMate

logger = logging.getLogger(__name__)

if not settings.DEBUG:
    from datadog import statsd


    @receiver(post_save, sender=Enrollment)
    def enrollment_metrics(sender: Enrollment, instance: Enrollment, created: bool, **kwargs):
        metric = "ceitba.enrollment.%s.count" % instance.service.name
        count = instance.service.enrollment_set.filter(date_removed__isnull=True).count()
        statsd.gauge(metric, count)


    @receiver(post_save, sender=PurchaseItem)
    def purchaseitem_metrics(sender: PurchaseItem, instance: PurchaseItem, created: bool, **kwargs):
        metric = "ceitba.purchaseitem.%s.count" % instance.product.name
        count = instance.quantity
        statsd.histogram(metric, count)


    @receiver(post_save, sender=AlquilerMate)
    def mates_metrics(sender: AlquilerMate, instance: AlquilerMate, created: bool, **kwargs):
        if created:
            statsd.increment("ceitba.mates.count")
        elif instance.time_returned is not None:
            time = instance.time_returned - instance.time_taken
            statsd.histogram("ceitba.mates.time", time)


@receiver(pre_social_login)
def user_logged_in(request, sociallogin, **kwargs):
    logger.info("User logged in: %s" % sociallogin.user.email)

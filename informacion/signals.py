import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from facturacion.models import Student
from informacion.models import PrinterCount

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Student)
def create_userdata_from_registration(sender, instance, created: bool, **kwargs):
    if created:
        printercount = PrinterCount(member=instance)
        printercount.save()
        logger.info("Created PrinterCount instance for member %s", instance)

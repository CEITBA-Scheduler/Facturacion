import datetime

from django.core.management.base import BaseCommand

from informacion.models import PrinterCount


class Command(BaseCommand):
    help = 'Imports the students csv file the database.'

    def handle(self, *args, **options):
        PrinterCount.objects.update(print_count=0)
        PrinterCount.objects.update(last_updated=datetime.datetime(2017, 9, 17, 0, 0, 0, 0))

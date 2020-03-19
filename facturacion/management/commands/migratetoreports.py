import datetime

from django.core.management.base import BaseCommand
from facturacion.models import Purchase, Report, Enrollment

EXCLUDED_DATES = [datetime.date(2016, 3, 21), datetime.date(2016, 3, 22)]


class Command(BaseCommand):
    help = 'Migrates the database to reports'

    def handle(self, *args, **options):

        if Report.objects.count()!=1:
            self.stdout.write(self.style.ERROR('Only one report can exist!'))
            return

        self.migrate_purchases()
        self.migrate_enrollments()

    def migrate_purchases(self):
        if Purchase.objects.filter(reported_in__isnull=False).count() > 0:
            self.stdout.write(self.style.ERROR('A report already exists. Database is inconsistent!'))
            return

        purchases = Purchase.objects.exclude(date_created__in=EXCLUDED_DATES).filter(reported_in__isnull=True)

        last_report = Report.objects.latest()

        num = purchases.update(reported_in=last_report)

        self.stdout.write(self.style.SUCCESS('Updated %d purchases!' % num))

    def migrate_enrollments(self):
        if Enrollment.objects.filter(reported_in__isnull=False).count() > 0:
            self.stdout.write(self.style.ERROR('A report already exists. Database is inconsistent!'))
            return

        enrollments = Enrollment.objects.exclude(date_created__in=EXCLUDED_DATES).filter(reported_in__isnull=True)

        last_report = Report.objects.latest()

        num = enrollments.update(reported_in=last_report)

        self.stdout.write(self.style.SUCCESS('Updated %d enrollments!' % num))
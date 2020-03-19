from constance import config
from django.core.management.base import BaseCommand

from facturacion.models import Enrollment
from informacion.models import SportCertificate


class Command(BaseCommand):
    help = 'Imports the students csv file the database.'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        enrollments = Enrollment.active.filter(
            service__name=config.GIMNASIO_SERVICE_NAME
        ).select_related('student')

        for enrollment in enrollments.iterator():

            sport_certificate = SportCertificate.objects.filter(member=enrollment.student)

            if not enrollment.student.email:
                continue

            if not sport_certificate.exists():
                self.stdout.write(
                    self.style.ERROR('%s' % (enrollment.student.email)))
                continue

            has_valid_certificate = SportCertificate.objects.filter(member=enrollment.student).latest().is_valid()

            if not sport_certificate.latest().is_valid():
                self.stdout.write(
                    self.style.ERROR('%s' % (enrollment.student.email)))

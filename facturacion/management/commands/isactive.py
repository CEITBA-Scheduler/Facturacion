import csv

from constance import config
from django.core.management.base import BaseCommand

from facturacion.models import Student, Service


class Command(BaseCommand):
    help = 'Imports the students csv file the database.'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        with open(options['file'], 'r') as csvfile:
            students = csv.reader(csvfile, delimiter=',')
            num = 0

            ceitba_service = Service.objects.get(name=config.CEITBA_SERVICE_NAME)

            for row in students:

                student = Student.objects.filter(student_id=row[0])

                if not student.exists():
                    continue

                student = student.get()

                enrollments = student.enrollment_set.filter(service=ceitba_service, date_removed__isnull=True)

                if not enrollments.exists():
                    self.stdout.write(self.style.WARNING('%s' % student.email or str(student.name)))
                    continue


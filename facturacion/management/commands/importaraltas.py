import csv
import datetime

from constance import config
from django.core.management.base import BaseCommand

from facturacion.models import Student, Enrollment, Service


class Command(BaseCommand):
    help = 'Creates the CEITBA enrollment for all previously active students'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        with open(options['file'], 'rb') as csvfile:
            students = csv.reader(csvfile)
            num = 0

            ceitba_service = Service.objects.get(name=config.CEITBA_SERVICE_NAME)

            for row in students:
                try:
                    student = Student.objects.get(student_id=row[0])

                    enrollment = Enrollment(student=student, service=ceitba_service)
                    enrollment.date_created = datetime.date(2016, 3, 15)

                    enrollment.save()

                except Student.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        u'Student with ID = %s, Name = %s does not exist' % (row[0], row[1].decode('utf-8'))))

                num += 1

                if num % 100 == 0:
                    self.stdout.write(self.style.NOTICE('Updated %d students so far' % num))

            self.stdout.write(self.style.SUCCESS('Update finished!\n\tUpdated %d students' % num))

import csv

from constance import config
from django.core.management.base import BaseCommand

from facturacion.models import Student, Enrollment, Service


class Command(BaseCommand):
    help = 'Creates the CEITBA enrollment for all previously active students'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        with open(options['file'], 'r') as csvfile:
            students = csv.reader(csvfile)
            num = 0
            alt = 0
            noexist = 0

            ymca_service = Service.objects.get(name=config.YMCA_SERVICE_NAME)

            for row in students:
                try:
                    student = Student.objects.get(student_id=row[0])

                    if not Enrollment.active.filter(student=student, service=ymca_service).exists():
                        # enrollment = Enrollment(student=student, service=ymca_service)
                        # enrollment.date_created = datetime.date(2016, 1, 1)
                        #
                        # enrollment.save()
                        alt += 1

                        self.stdout.write(self.style.ERROR(
                            'El estudiante con legajo %s no esta suscripto al YMCA.' % (row[0],)))

                except Student.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        'ERROR: El estudiante con legajo %s no EXISTE.' % (row[0],)))
                    noexist += 1

                except ValueError:
                    print('ERROR' + row)

                num += 1

            self.stdout.write(self.style.SUCCESS(
                'Update finished!\n\tUpdated %d/%d students. %d no existentes' % (alt, num, noexist)))

import csv

from django.core.management.base import BaseCommand

from facturacion.models import Student


class Command(BaseCommand):
    help = 'Creates the CEITBA enrollment for all previously active students'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        with open(options['file'], 'r') as csvfile:
            students = csv.reader(csvfile, delimiter=',')
            num = 0

            for row in students:
                student = Student.objects.filter(student_id=row[0])

                if not student.exists():
                    new_student = Student(name=row[1])
                    new_student.student_id = row[0]
                    new_student.dni=row[2]
                    new_student.save(add_ceitba_enrollment=True)

                num += 1

                if num % 100 == 0:
                    self.stdout.write(self.style.NOTICE('Added %d students so far' % num))

            self.stdout.write(self.style.SUCCESS('Update finished!\n\tUpdated %d students' % num))

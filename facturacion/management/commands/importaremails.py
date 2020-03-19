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

                students = Student.objects.filter(name__icontains=row[1]).filter(name__icontains=row[2])

                if students.count() != 1:
                    self.stdout.write(
                        self.style.ERROR(
                            u'Student with LastName = %s, Name = %s does not exist' % (
                                row[2], row[1])))
                    continue

                student = students.get()

                student.email = row[3]

                student.clean()

                student.save()

                num += 1

            if num % 100 == 0:
                self.stdout.write(self.style.NOTICE('Updated %d students so far' % num))

        self.stdout.write(self.style.SUCCESS('Update finished!\n\tUpdated %d students' % num))

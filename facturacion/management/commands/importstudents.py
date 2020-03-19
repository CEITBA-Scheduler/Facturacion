from django.core.management.base import BaseCommand
from facturacion.models import Student
import csv


class Command(BaseCommand):
    help = 'Imports the students csv file the database.'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        with open(options['file'], 'r') as csvfile:
            students = csv.reader(csvfile, delimiter=',')
            num = 0
            for row in students:

                student_exist = Student.objects.filter(student_id=row[0]).exists()

                if student_exist:
                    self.stdout.write(self.style.WARNING('Student [%s] %s already exists' % (row[0], row[1])))
                    continue

                student = Student(name=row[1])
                student.student_id = row[0]
                student.save(add_ceitba_enrollment=False)
                num += 1
                if num % 100 == 0:
                    self.stdout.write(self.style.NOTICE('Imported %d students so far' % num))

            self.stdout.write(self.style.SUCCESS('Import finished!\n\tImported %d students' % num))

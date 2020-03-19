from django.core.management.base import BaseCommand
from facturacion.models import Student
from nautica.models import Authorization
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

                first = row[0].strip()
                last = row[1].strip()

                students = Student.objects.filter(name__contains=first).filter(name__contains=last)

                if not students.exists() or students.count() > 1:
                    self.stdout.write(
                        self.style.WARNING('Unique student not found. FIRST_NAME="%s" LAST_NAME="%s"' % (first, last)))
                    continue

                student = students.get()

                auth = Authorization()
                auth.member = student
                auth.dni = row[2].strip()

                type_row = row[3]

                if type_row == "timonel":
                    auth.auth_type = Authorization.TYPE_TIMONEL
                elif type_row == 'patron':
                    auth.auth_type == Authorization.TYPE_PATRON

                auth.save()

                num += 1
                if num % 100 == 0:
                    self.stdout.write(self.style.NOTICE('Imported %d students so far' % num))

            self.stdout.write(self.style.SUCCESS('Import finished!\n\tImported %d students' % num))

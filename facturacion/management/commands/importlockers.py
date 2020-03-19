import csv
import traceback

from django.core.management.base import BaseCommand

from facturacion.models import Student, Service, Enrollment
from lockers.models import LockerAssignation


class Command(BaseCommand):
    help = 'Imports lockers'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', nargs='?', type=str)
        parser.add_argument('service', nargs='?', type=str)

    def handle(self, file, *args, **options):

        try:
            locker_service = Service.objects.get(name=options['service'])

            locker_site = locker_service.lockersite
        except Service.DoesNotExist:
            self.stderr.write(self.style.ERROR("Service does not exist: %s" % options['service']))
            return

        with open(file, 'r') as csvfile:
            students = csv.reader(csvfile, delimiter=',')
            num = 0

            for row in students:
                try:
                    student = Student.objects.get(student_id=row[1])

                    enrollment = student.enrollment_set.filter(service=locker_site.service, date_removed__isnull=True)

                    if enrollment.count() > 1:
                        self.stdout.write(
                            self.style.NOTICE('Student has more than one locker enrollment: %s' % student))
                        continue

                    e = enrollment.get()

                    assignation = LockerAssignation()
                    assignation.enrollment = e
                    assignation.locker_id = row[0]
                    assignation.save()

                    # LockerAssignation.create_assignation(student, locker_site, row[0])

                except Student.DoesNotExist:
                    self.stdout.write(
                        self.style.SUCCESS(
                            u'Student with ID = %s does not exist' % row[1]))
                    return

                except Enrollment.DoesNotExist as err:
                    traceback.print_tb(err.__traceback__)
                    self.stdout.write(
                        self.style.SUCCESS(
                            u'Error with Student with ID = %s' % row[1]))
                    return

                except Exception as err:
                    traceback.print_tb(err.__traceback__)
                    self.stdout.write(str(err))
                    self.stdout.write(
                        self.style.ERROR(
                            u'Error with student ID = %s' % row[1]))
                    return

                num += 1

                self.stdout.write(self.style.NOTICE('Updated %d students so far' % num))

            self.stdout.write(self.style.SUCCESS('Update finished!\n\tUpdated %d students' % num))

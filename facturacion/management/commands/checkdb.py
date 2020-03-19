from constance import config
from django.core.management.base import BaseCommand

from facturacion.models import Student, Service, Enrollment
from lockers.models import LockerAssignation, LockerSite


class Command(BaseCommand):
    help = 'Migrates the database to reports'

    def handle(self, *args, **options):

        ceitba_service = Service.objects.filter(name__exact=config.CEITBA_SERVICE_NAME).get()
        ymca_service = Service.objects.filter(name__exact=config.YMCA_SERVICE_NAME).get()

        for student in Student.objects.iterator():

            other_enrollments = student.enrollment_set.exclude(service=ceitba_service)

            if other_enrollments.count() > 0:

                if other_enrollments.filter(service__type=Service.LOCKER, date_removed__isnull=True).count() > 1:
                    for en in other_enrollments.filter(service__type=Service.LOCKER, date_removed__isnull=True):
                        self.stdout.write(
                            self.style.NOTICE('(%d) %s @ %s' % (en.student.student_id, en.student.name, en.service)))

        lockersites = LockerSite.objects.all()

        assignations = LockerAssignation.objects.all()

        enrollments = Enrollment.objects.filter(
            service__type=Service.LOCKER,
            service__lockersite__in=lockersites,
            date_removed__isnull=True
        ).exclude(lockerassignation__in=assignations)

        for e in enrollments:
            self.stdout.write(self.style.NOTICE('(%d) %s @ %s' % (e.student.student_id, e.student.name, e.service)))

from constance import config
from django.core.management.base import BaseCommand

from facturacion.models import Student, Service, Reimbursement


class Command(BaseCommand):
    help = 'Migrates the database to reports'

    def handle(self, *args, **options):

        ceitba_service = Service.objects.filter(name__exact=config.CEITBA_SERVICE_NAME).get()

        for student in Student.objects.iterator():

            enrollments = student.enrollment_set.filter(service=ceitba_service, date_removed__isnull=True)

            if enrollments.count() > 1:
                self.stdout.write(
                    self.style.NOTICE('Student (%d) %s is suscribed %i times to CEITBA' % (
                        student.student_id, student.name, enrollments.count())))

                one_enrollment = enrollments.first()

                self.stdout.write("Keeping %s" % one_enrollment.pk)

                to_delete = enrollments.exclude(pk=one_enrollment.pk)
                self.stdout.write("Deleting %s" % to_delete.get().pk)

                to_delete.delete()

                reimbursement = Reimbursement()
                reimbursement.student = student
                reimbursement.amount = ceitba_service.price * 2
                reimbursement.concept = "Error de la DB. Reembolso automatico"
                reimbursement.save()

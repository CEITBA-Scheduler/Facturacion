import datetime
import logging
import sys

from constance import config
from django.test import TestCase

from facturacion.models import Service, Student, Enrollment, Report, Product

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)

TEST_STUDENT_ID = 12345

TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100),
                 (config.YMCA_SERVICE_NAME, 10),
                 ('Gimnasio', 15),
                 ('Lockers Entrepiso', 20)]


class TestService(TestCase):
    @classmethod
    def setUpTestData(cls):
        for service, price in TEST_SERVICES:
            logger.info("Adding service %s" % service)
            s = Service(name=service, price=price)
            s.save()

        product = Product(name=config.IMPRESIONES_PRODUCT, price=10)
        product.save()

    def test_deletion(self):
        """
        Testea que al eliminar un servicio, su fecha de remocion se setee en la actual en lugar de ser eliminado
        :return:
        """
        services = Service.objects.filter(name=config.YMCA_SERVICE_NAME)

        self.assertEqual(1, services.count())

        service = services.get()
        service.delete()

        self.assertIsNotNone(service.date_removed)

    def test_deletion_cascade(self):
        """
        Testea que al eliminar un servicio, todas las suscripciones al mismo sean dadas de baja
        :return:
        """
        ymca_service = Service.objects.get(name=config.YMCA_SERVICE_NAME)

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        enrollment = Enrollment(service=ymca_service, student=student)
        enrollment.date_created = datetime.date(2016, 1, 1)  # Para evitar same_day deletion
        enrollment.save()

        enrollments = student.enrollment_set.all()

        # Nos aseguramos que existan dos suscripciones, la del YMCA y la del CEITBA
        self.assertEqual(2, enrollments.count())

        report = Report()
        report.save()

        # Borramos el servicio
        ymca_service.delete()

        ymca_enrollment = Enrollment.objects.get(service__name=config.YMCA_SERVICE_NAME)

        self.assertEqual(ymca_enrollment.date_removed, datetime.date.today())

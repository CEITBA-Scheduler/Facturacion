import logging
import sys
from datetime import date

from constance import config
from django.test import TestCase

from facturacion.models import Enrollment, Student, Service, Product, Purchase, PurchaseItem, Report, Debt

TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100),
                 (config.YMCA_SERVICE_NAME, 10),
                 ('Gimnasio', 15),
                 ('Lockers Entrepiso', 20)]

TEST_PRODUCTS = [('Cuaderno', 25),
                 ('Taza', 40),
                 ('Examen Medico', 450),
                 (config.IMPRESIONES_PRODUCT, 100)]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)

TEST_STUDENT_NAME = "Test Name"
TEST_STUDENT_ID = "12345"


class TestReports(TestCase):
    @classmethod
    def setUpTestData(cls):
        # FIXME
        pass
        for service, price in TEST_SERVICES:
            logger.info("Adding service %s" % service)
            s = Service(name=service, price=price)
            s.save()

        for product, price in TEST_PRODUCTS:
            logger.info("Adding product %s" % product)
            p = Product(name=product, price=price)
            p.save()

    def test_report_creation(self):
        # FIXME
        pass
        student = Student(name=TEST_STUDENT_NAME, student_id=TEST_STUDENT_ID)
        student.save()
        student = Student.objects.get()
        # Costo suscripcion ceitba por defecto = 100

        enrollment = Enrollment(student=student,
                                service=Service.objects.filter(name=config.YMCA_SERVICE_NAME).get())
        enrollment.save()  # Cuesta 10

        enrollment2 = Enrollment(student=student,
                                 service=Service.objects.filter(name='Gimnasio').get())
        enrollment2.save()  # Cuesta 15

        # Costo de suscripciones hasta aca: 25

        for e in Enrollment.objects.all():
            print(e.service.name + '=' + str(e.service.price))

        purchase1 = Purchase(student=student)
        purchase1.save()

        purchaseitem1 = PurchaseItem(purchase=purchase1, product=Product.objects.filter(name='Cuaderno').get(),
                                     quantity=2)
        purchaseitem1.save()  # Costo: 2* 25=50

        purchaseitem1 = PurchaseItem(purchase=purchase1, product=Product.objects.filter(name='Taza').get(), quantity=3)
        purchaseitem1.save()  # Costo: 3* 40=120

        for item in PurchaseItem.objects.all():
            print(item.product.name + '=' + str(item.product.price) + "*" + str(item.quantity))

        # Costo compra 1 : 170

        report = Report()
        report.save()

        # 100 + 25 + 170 = 295

        self.assertEqual(report.totalin, 295)
        self.assertEqual(report.totalout, 0)
        self.assertEqual(report.students, 1)
        self.assertEqual(report.active_members, 1)
        self.assertEqual(report.subscriptions, 1)
        self.assertEqual(report.unsubscriptions, 0)

    def test_debt_creation(self):

        student = Student(name=TEST_STUDENT_NAME, student_id=TEST_STUDENT_ID)
        student.save()

        enrollment = Enrollment()
        enrollment.service = Service.objects.get(name=config.YMCA_SERVICE_NAME)
        enrollment.student = student
        enrollment.billable = False
        enrollment.save()

        self.assertIsNotNone(enrollment.pk)

        report = Report()
        report.save()

        debts = Debt.objects.filter(student=student)

        self.assertEqual(debts.count(), 1)

        debt = debts.get()

        self.assertEqual(debt.student.pk, student.pk)

        enrollments = debt.enrollments

        self.assertEqual(enrollments.count(), 1)

        debt_enrollment = enrollments.get()

        self.assertEqual(debt_enrollment.pk, enrollment.pk)

        self.assertEqual(debt.amount, enrollment.service.price)

        self.assertFalse(debt.is_paid)

        debt.date_paid = date.today()
        debt.save()

        self.assertTrue(debt.is_paid)

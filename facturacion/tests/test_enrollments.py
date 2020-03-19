import logging
import sys

from constance import config
from django.core.exceptions import ValidationError
from django.test import TestCase

from facturacion.models import Enrollment, Student, Service, Product, Purchase

TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100),
                 (config.YMCA_SERVICE_NAME, 10),
                 ('Gimnasio', 15),
                 ('Lockers Entrepiso', 20)]
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)

TEST_STUDENT_ID = 12345


class TestEnrollments(TestCase):
    @classmethod
    def setUpTestData(cls):
        for service, price in TEST_SERVICES:
            logger.info("Adding service %s" % service)
            s = Service(name=service, price=price)
            s.save()

    def test_auto_ceitba_enrollment(self):
        """
        Test de que cuando se crea un alumno, automaticamente se lo suscribe al CEITBA
        :return:
        """

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        student = Student.objects.filter(student_id=TEST_STUDENT_ID).get()

        enrollments = Enrollment.objects.filter(student__student_id=student.student_id)
        enrollment = enrollments.get()

        self.assertEqual(enrollments.count(), 1)
        self.assertEqual(enrollment.student.student_id, student.student_id)
        self.assertEqual(enrollment.service.name, config.CEITBA_SERVICE_NAME)
        self.assertTrue(enrollment.is_active())

    def test_same_day_deletion(self):
        """
        Test de que al crear y eliminar una suscripcion en el mismo dia, esta de elimina de forma definitiva
        :return:
        """

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        student = Student.objects.filter(student_id=TEST_STUDENT_ID).get()

        enrollment = Enrollment.objects.filter(student__student_id=student.student_id).get()
        enrollment.delete()

        enrollments = Enrollment.objects.filter(student__student_id=student.student_id)

        self.assertEqual(enrollments.count(), 0)

    def test_auto_ceitba_enrollment_cascade(self):
        """
        Test de que cuando se suscribe a un alumno a otro servicio, automaticamente se lo suscribe
        al CEITBA
        :return:
        """

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        student = Student.objects.filter(student_id=TEST_STUDENT_ID).get()

        # Primero eliminamos la suscripcion
        Enrollment.objects.filter(student__student_id=TEST_STUDENT_ID).delete()

        enrollments = Enrollment.objects.filter(student__student_id=TEST_STUDENT_ID)
        self.assertEqual(enrollments.count(), 0)

        ymca_service = Service.objects.get(name=config.YMCA_SERVICE_NAME)

        enrollment = Enrollment(service=ymca_service, student=student)
        enrollment.save()

        # Test for CEITBA enrollment
        ceitba_enrollments = Enrollment.objects.filter(student__student_id=TEST_STUDENT_ID,
                                                       service__name=config.CEITBA_SERVICE_NAME)
        self.assertEqual(ceitba_enrollments.count(), 1)

        ceitba_enrollment = ceitba_enrollments.get()

        self.assertEqual(ceitba_enrollment.service.name, config.CEITBA_SERVICE_NAME)
        self.assertEqual(ceitba_enrollment.student.student_id, TEST_STUDENT_ID)

        # Test for YMCA enrollment
        ymca_enrollments = Enrollment.objects.filter(student__student_id=TEST_STUDENT_ID,
                                                     service__name=config.YMCA_SERVICE_NAME)
        self.assertEqual(ymca_enrollments.count(), 1)
        ymca_enrollment = ymca_enrollments.get()

        self.assertEqual(ymca_enrollment.service.name, config.YMCA_SERVICE_NAME)
        self.assertEqual(ymca_enrollment.student.student_id, TEST_STUDENT_ID)

    def test_auto_deletion_cascade(self):
        """
        Test de que cuando se desuscribe el servicio CEITBA, automaticamente
        se desuscribe del resto de los servicios en cascada
        :return:
        """

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        student = Student.objects.filter(student_id=TEST_STUDENT_ID).get()
        ymca_service = Service.objects.get(name=config.YMCA_SERVICE_NAME)

        enrollment = Enrollment(service=ymca_service, student=student)
        enrollment.save()

        ceitba_enrollments = Enrollment.objects.filter(student=student, service__name=config.CEITBA_SERVICE_NAME)

        self.assertEqual(1, ceitba_enrollments.count())

        ceitba_enrollment = ceitba_enrollments.get()
        ceitba_enrollment.delete()

        enrollments = student.enrollment_set.all()

        self.assertEqual(0, enrollments.count())

    def test_single_subscription_success(self):
        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        service_gim = Service.objects.get(name='Gimnasio')
        service_gim.single_subscription = False
        service_gim.save()

        enrollment = Enrollment(service=service_gim, student=student)
        enrollment.full_clean()
        enrollment.save()

        self.assertIsNotNone(enrollment.pk)

        enrollment2 = Enrollment(service=service_gim, student=student)
        enrollment2.full_clean()
        enrollment2.save()

        self.assertIsNotNone(enrollment2.pk)

    def test_single_subscription_fail(self):
        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        service_gim = Service.objects.get(name='Gimnasio')

        enrollment = Enrollment(service=service_gim, student=student)
        enrollment.full_clean()
        enrollment.save()

        self.assertIsNotNone(enrollment.pk)

        enrollment2 = Enrollment(service=service_gim, student=student)

        with self.assertRaises(ValidationError):
            enrollment2.full_clean()

    def test_auto_add_exam_fail(self):
        product = Product(name=config.YMCA_MEDICALEXAM_PRODUCT_NAME, price=10)
        product.save()

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        service_ymca = Service.objects.get(name=config.YMCA_SERVICE_NAME)

        enrollment = Enrollment(student=student, service=service_ymca)
        enrollment.save(add_ymca_medical_exam=False)

        self.assertIsNotNone(enrollment.pk)

        purchases = Purchase.objects.filter(student=student)

        self.assertEqual(purchases.count(), 0)

    def test_auto_add_exam_success(self):
        product = Product(name=config.YMCA_MEDICALEXAM_PRODUCT_NAME, price=10)
        product.save()

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        service_ymca = Service.objects.get(name=config.YMCA_SERVICE_NAME)

        enrollment = Enrollment(student=student, service=service_ymca)
        enrollment.save(add_ymca_medical_exam=True)

        self.assertIsNotNone(enrollment.pk)

        purchases = Purchase.objects.filter(student=student)

        self.assertEqual(purchases.count(), 1)

        purchase = purchases.get()

        purchaseitems = purchase.purchaseitem_set

        self.assertEqual(purchaseitems.count(), 1)

        purchaseitem = purchaseitems.get()

        self.assertEqual(purchaseitem.product.pk, product.pk)
        self.assertEqual(purchaseitem.quantity, 1)

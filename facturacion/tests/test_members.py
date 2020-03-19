from constance import config
from django.core.exceptions import ValidationError
from django.test import TestCase

from facturacion.models import Student, Service

STUDENT_NAME = "Test Name"
STUDENT_ID = "12345"

STUDENT_VALID_EMAIL = "test@itba.edu.ar"
STUDENT_INVALID_EMAIL = "test@gmail.com"

TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100), ]


class TestMembers(TestCase):
    @classmethod
    def setUpTestData(cls):
        for service, price in TEST_SERVICES:
            s = Service(name=service, price=price)
            s.save()

    def test_member_valid_email(self):
        student = Student()
        student.name = STUDENT_NAME
        student.student_id = STUDENT_ID
        student.email = STUDENT_VALID_EMAIL

        student.full_clean()
        student.save()

        self.assertIsNotNone(student.pk)
        self.assertTrue(student.is_active())

    def test_member_invalid_mail(self):
        student = Student()
        student.name = STUDENT_NAME
        student.student_id = STUDENT_ID
        student.email = STUDENT_INVALID_EMAIL

        with self.assertRaises(ValidationError):
            student.full_clean()

    def test_member_remove(self):
        student = Student()
        student.name = STUDENT_NAME
        student.student_id = STUDENT_ID
        student.email = STUDENT_VALID_EMAIL

        student.full_clean()
        student.save()

        self.assertIsNotNone(student.pk)
        self.assertIsNone(student.date_removed)

        student.delete()

        self.assertIsNotNone(student.date_removed)

import logging
import sys

from constance import config
from django.core.exceptions import ValidationError
from django.test import TestCase

from facturacion.models import Service, Student, Enrollment
from lockers.models import LockerSite, LockerAssignation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)

TEST_STUDENT_ID = 12345

LOCKER_SERVICE_NAME = 'Lockers Entrepiso'

TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100),
                 (LOCKER_SERVICE_NAME, 20)]


class TestService(TestCase):
    @classmethod
    def setUpTestData(cls):
        for service, price in TEST_SERVICES:
            logger.info("Adding service %s" % service)
            s = Service(name=service, price=price)
            s.save()

        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        new_lockersite = LockerSite(count=10)
        new_lockersite.service = locker_service

        new_lockersite.save()

        print("Added lockersite %s (%d)" % (new_lockersite, new_lockersite.count))

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        Enrollment(service=locker_service, student=student).save()

    def test_add_assignation(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        locker_enrollments = Enrollment.objects.filter(service=locker_service)

        self.assertEqual(1, locker_enrollments.count())

        new_assignation = LockerAssignation()
        new_assignation.enrollment = locker_enrollments.get()
        new_assignation.locker_id = 4
        new_assignation.save()

        lockersite = locker_service.lockersite

        self.assertEqual(9, lockersite.free_spots())
        self.assertTrue(lockersite.has_free_spots())
        self.assertEqual(1, lockersite.get_free_locker())
        self.assertEqual(1, lockersite.used_spots())

    def test_add_assignation_used(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        locker_enrollments = Enrollment.objects.filter(service=locker_service)

        self.assertEqual(1, locker_enrollments.count())

        new_assignation = LockerAssignation()
        new_assignation.enrollment = locker_enrollments.get()
        new_assignation.locker_id = 4
        new_assignation.full_clean()
        new_assignation.save()

        new_assignation = LockerAssignation()
        new_assignation.enrollment = locker_enrollments.get()
        new_assignation.locker_id = 4

        with self.assertRaises(ValidationError):
            new_assignation.full_clean()

    def test_invalid_lockerid(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        locker_enrollments = Enrollment.objects.filter(service=locker_service)

        lockersite = locker_service.lockersite

        self.assertEqual(10, lockersite.free_spots())
        self.assertEqual(10, locker_enrollments.get().service.lockersite.count)

        with self.assertRaises(ValidationError):
            new_assignation = LockerAssignation()
            new_assignation.enrollment = locker_enrollments.get()
            new_assignation.locker_id = 15
            new_assignation.clean()
            new_assignation.save()

        self.assertEqual(10, lockersite.free_spots())
        self.assertTrue(lockersite.has_free_spots())
        self.assertEqual(1, lockersite.get_free_locker())
        self.assertEqual(0, lockersite.used_spots())

    def test_assigned_locker(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        locker_enrollments = Enrollment.objects.filter(service=locker_service)

        self.assertEqual(1, locker_enrollments.count())

        lockersite = locker_service.lockersite

        self.assertEqual(10, lockersite.free_spots())
        self.assertEqual(10, locker_enrollments.get().service.lockersite.count)

        new_assignation = LockerAssignation()
        new_assignation.enrollment = locker_enrollments.get()
        new_assignation.locker_id = 1
        new_assignation.clean()
        new_assignation.save()

        # por @cached_property, tenemos que actualizar lockersite
        lockersite = Service.objects.filter(name=LOCKER_SERVICE_NAME).get().lockersite

        self.assertEqual(9, lockersite.free_spots())
        self.assertTrue(lockersite.has_free_spots())
        self.assertEqual(2, lockersite.get_free_locker())
        self.assertEqual(1, lockersite.used_spots())

        new_student = Student(name='Test Student 2', student_id=TEST_STUDENT_ID + 1)
        new_student.save()

        new_enrollment = Enrollment(service=locker_service, student=new_student)
        new_enrollment.save()

        new_assignation = LockerAssignation()
        new_assignation.enrollment = new_enrollment
        new_assignation.locker_id = lockersite.get_free_locker()
        new_assignation.clean()
        new_assignation.save()

        # por @cached_property, tenemos que actualizar lockersite
        lockersite = Service.objects.filter(name=LOCKER_SERVICE_NAME).get().lockersite

        self.assertEqual(8, lockersite.free_spots())
        self.assertTrue(lockersite.has_free_spots())
        self.assertEqual(3, lockersite.get_free_locker())
        self.assertEqual(2, lockersite.used_spots())

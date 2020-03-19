import logging
import sys

from constance import config
from django.test import TestCase

from facturacion.models import Service, Student
from lockers.models import LockerSite, LockerAssignation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)

TEST_STUDENT_ID = 12345

LOCKER_SERVICE_NAME = 'Lockers Entrepiso'

TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100),
                 (LOCKER_SERVICE_NAME, 20)]


class TestLockerSite(TestCase):
    @classmethod
    def setUpTestData(cls):
        for service, price in TEST_SERVICES:
            logger.info("Adding service %s" % service)
            s = Service(name=service, price=price)
            s.save()

    def test_add_lockersite(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        new_lockersite = LockerSite(count=100)
        new_lockersite.service = locker_service

        new_lockersite.save()

        lockersites = LockerSite.objects.all()

        self.assertEqual(1, lockersites.count())

        lockersite = lockersites.get()

        self.assertEqual(100, lockersite.count)
        self.assertEqual(locker_service, lockersite.service)

        self.assertEqual(100, lockersite.free_spots())
        self.assertTrue(lockersite.has_free_spots())
        self.assertEqual(1, lockersite.get_free_locker())
        self.assertEqual(0, lockersite.used_spots())

    def test_empty_lockersute(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        new_lockersite = LockerSite(count=3)
        new_lockersite.service = locker_service

        new_lockersite.save()

        self.assertEqual(new_lockersite.get_free_locker(), 1)

        new_assignation, new_enrollment = LockerAssignation.create_assignation(student, new_lockersite, 2)

        self.assertEqual(new_lockersite.get_free_locker(), 1)

        new_assignation, new_enrollment = LockerAssignation.create_assignation(student, new_lockersite, 1)

        self.assertEqual(new_lockersite.get_free_locker(), 3)

        new_assignation, new_enrollment = LockerAssignation.create_assignation(student, new_lockersite, 3)

        self.assertEqual(new_lockersite.get_free_locker(), None)
        self.assertEqual(new_lockersite.free_spots(), 0)

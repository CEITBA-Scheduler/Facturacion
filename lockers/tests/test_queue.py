import logging
import sys

from constance import config
from django.core.exceptions import ValidationError
from django.test import TestCase

from facturacion.models import Service, Student
from lockers.models import LockerSite, LockerAssignation, LockerQueue, LockerHold

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)

TEST_STUDENT_ID = 12345

LOCKER_SERVICE_NAME = 'Lockers Entrepiso'

TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100),
                 (LOCKER_SERVICE_NAME, 20)]


class TestQueue(TestCase):
    @classmethod
    def setUpTestData(cls):
        config.LOCKER_ENABLE_AUTOHOLD = False

        for service, price in TEST_SERVICES:
            logger.info("Adding service %s" % service)
            s = Service(name=service, price=price)
            s.save()

    def test_add_queueitem_success(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        new_lockersite = LockerSite(count=100)
        new_lockersite.service = locker_service
        new_lockersite.save()

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        queueitem = LockerQueue(locker_site=new_lockersite, member=student)
        queueitem.full_clean()
        queueitem.save()

        self.assertIsNotNone(queueitem.pk)

    def test_add_queueitem_already_in_queue(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        new_lockersite = LockerSite(count=100)
        new_lockersite.service = locker_service
        new_lockersite.save()

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        queueitem = LockerQueue(locker_site=new_lockersite, member=student)
        queueitem.full_clean()
        queueitem.save()

        self.assertIsNotNone(queueitem.pk)

        queueitem = LockerQueue(locker_site=new_lockersite, member=student)
        with self.assertRaises(ValidationError):
            queueitem.full_clean()

    def test_add_queueitem_in_hold(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        new_lockersite = LockerSite(count=100)
        new_lockersite.service = locker_service
        new_lockersite.save()

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        lockerhold = LockerHold(locker_site=new_lockersite, member=student, locker_id=1)
        lockerhold.full_clean()
        lockerhold.save()

        self.assertIsNotNone(lockerhold.pk)

        queueitem = LockerQueue(locker_site=new_lockersite, member=student)
        with self.assertRaises(ValidationError):
            queueitem.full_clean()

    def test_add_queueitem_has_locker(self):
        locker_service = Service.objects.filter(name=LOCKER_SERVICE_NAME).get()

        new_lockersite = LockerSite(count=100)
        new_lockersite.service = locker_service
        new_lockersite.save()

        student = Student(name='Test Student', student_id=TEST_STUDENT_ID)
        student.save()

        new_assignation, new_enrollment = LockerAssignation.create_assignation(student, new_lockersite, 2)

        queueitem = LockerQueue(locker_site=new_lockersite, member=student)
        with self.assertRaises(ValidationError):
            queueitem.full_clean()

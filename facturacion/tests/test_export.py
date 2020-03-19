import datetime
import logging
import random
import shutil
import sys

from constance import config
from django.test import TestCase

from facturacion.export import generate_spreadsheet
from facturacion.models import Service, Student, Product, Enrollment, PurchaseItem, Purchase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)

PRODUCTS = ['Cuaderno', 'Taza', 'Birome']
TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100),
                 (config.YMCA_SERVICE_NAME, 10),
                 ('Gimnasio', 15),
                 ('Lockers Entrepiso', 20)]

ITERATIONS = 1000
START_RAND_YEAR = 2015
END_RAND_YEAR = 2016


def rand_date(start_year, end_year):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)


class TestExport(TestCase):
    @classmethod
    def setUpTestData(cls):

        logger.info('Populating database.')
        with open('./names.txt') as f:
            names = f.readlines()

        if names is None:
            raise Exception("Couldn't find names")

        random.seed()

        for service, price in TEST_SERVICES:
            logger.info("Adding service %s" % service)
            s = Service(name=service, price=price)
            s.save()

        for name, i in zip(names, range(0, len(names))):
            student = Student(name=name, date_created=rand_date(START_RAND_YEAR, END_RAND_YEAR))
            student.student_id = i
            student.save()

            # print "Added student %s" % student.name

        for product in PRODUCTS:
            p = Product(name=product, price=random.randint(1, 300))
            p.save()

    def test_system(self):
        for i in range(1, random.randint(1, ITERATIONS)):
            student = Student.objects.order_by('?').first()
            service = Service.objects.order_by('?').first()

            enrollment = Enrollment(student=student, service=service,
                                    date_created=rand_date(START_RAND_YEAR, END_RAND_YEAR),
                                    date_removed=rand_date(START_RAND_YEAR, END_RAND_YEAR))
            enrollment.save()

        for _ in range(1, random.randint(1, ITERATIONS)):
            student = Student.objects.order_by('?').first()
            purchase = Purchase(student=student, date_created=rand_date(START_RAND_YEAR, END_RAND_YEAR))
            purchase.save()

            for __ in range(1, random.randint(2, 10)):
                product = Product.objects.order_by('?').first()
                quantity = random.randint(2, 10)

                item = PurchaseItem(purchase=purchase, product=product, quantity=quantity)
                item.save()

    def tearDown(self):

        start_date = datetime.date(2015, 2, 1)
        end_date = datetime.date(2015, 4, 1)

        file_obj = generate_spreadsheet()

        filename = 'Test Export (%s - %s).xlsx' % (start_date, end_date)

        with open(filename, 'wb') as fd:
            file_obj.seek(0)
            shutil.copyfileobj(file_obj, fd)

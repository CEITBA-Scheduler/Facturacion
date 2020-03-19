import logging
import sys
from datetime import date

from constance import config
from django.test import TestCase

from facturacion.models import Product

TEST_PRODUCT = 'Cuaderno'
TEST_SERVICES = [(config.CEITBA_SERVICE_NAME, 100),
                 (config.YMCA_SERVICE_NAME, 10),
                 ('Gimnasio', 15),
                 ('Lockers Entrepiso', 20)]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)


class TestProducts(TestCase):
    def setUp(self):
        product = Product(name=TEST_PRODUCT, price=10)
        product.save()

    def test_deletion(self):
        products = Product.objects.filter(name=TEST_PRODUCT)

        self.assertEqual(1, products.count())

        product = products.get()

        self.assertTrue(product.is_active())

        product.delete()

        self.assertEqual(product.date_removed, date.today())

    def test_automatic_deactivation(self):
        products = Product.objects.filter(name=TEST_PRODUCT)

        self.assertEqual(1, products.count())

        product = products.get()

        self.assertEqual(TEST_PRODUCT, product.name)
        self.assertEqual(10, product.price)

        new_product = Product(name=TEST_PRODUCT, price=20)
        result = new_product.save()

        self.assertEqual(result, True)

        products = Product.active.filter(name=TEST_PRODUCT)
        self.assertEqual(1, products.count())
        product = products.get()

        self.assertEqual(TEST_PRODUCT, product.name)
        self.assertEqual(20, product.price)

        products = Product.objects.filter(name=TEST_PRODUCT)

        self.assertEqual(2, products.count())

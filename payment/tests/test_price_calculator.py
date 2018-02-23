from django.test import TestCase
from payment.helpers import PriceCalculator


class PriceCalculationsTest(TestCase):

    def setUp(self):
        self.instance = PriceCalculator()
        pass

    def test_PriceCalculation(self):

        self.fail('Test not implemented.')


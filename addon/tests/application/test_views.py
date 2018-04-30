"""
    Tests das Views
"""
from django.contrib.auth.models import User
from django.test.client import Client
from django.urls import reverse_lazy
from test_plus.test import TestCase

from addon.tests import MockFactory

fake_email = MockFactory().fake_factory.free_email()
password = 'mypassword'

test_user = User.objects.create_user(fake_email, fake_email, password)


class EventProductManagementViewTest(TestCase):

    def setUp(self):
        factory = MockFactory()
        self.c = Client()
        self.c.login(username=test_user.username, password=password)
        self.lot_category = factory.fake_lot_category()
        self.first_product = factory.fake_product(
            lot_category=self.lot_category)
        self.first_product.name = 'first_product'
        self.first_product.save()
        self.second_product = factory.fake_product(
            lot_category=self.lot_category)
        self.second_product.name = 'second_product'
        self.second_product.save()
        self.third_product = factory.fake_product(
            lot_category=self.lot_category)
        self.third_product.name = 'third_product'
        self.third_product.save()

    def test_get_requests_with_no_session_returns_all_optionals(self):
        response = self.c.get(path=reverse_lazy(
            'optional:available_optional_product_list', kwargs={
                'category_pk': self.lot_category.pk
            }))

        self.assertIs(response.status_code, 200)
        self.assertContains(response, self.first_product.name)
        self.assertContains(response, self.second_product.name)
        self.assertContains(response, self.third_product.name)

    def test_get_requests_with_session_returns_all_optionals_in_storage(self):
        s = self.c.session
        s.update({
            "product_storage": [self.first_product.pk, self.third_product.pk],
        })
        s.save()

        response = self.c.get(path=reverse_lazy(
            'optional:available_optional_product_list', kwargs={
                'category_pk': self.lot_category.pk
            }))

        self.assertIs(response.status_code, 200)
        self.assertContains(response, self.first_product.name)
        self.assertNotContains(response, self.second_product.name)
        self.assertContains(response, self.third_product.name)

    def test_post_requests_no_optional_id_sent(self):

        response = self.c.post(path=reverse_lazy(
            'optional:available_optional_product_list', kwargs={
                'category_pk': self.lot_category.pk
            }))

        self.assertIs(response.status_code, 400)

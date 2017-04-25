from django.test import TestCase

from django.db import IntegrityError
from gatheros_event.models import Event
from gatheros_subscription.models import Form


class FormModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event'
    ]

    def test_no_form_for_event_with_disabled_subscription(self):
        form = Form(event=Event.objects.filter(subscription_type=Event.SUBSCRIPTION_DISABLED).first())

        with self.assertRaises(IntegrityError):
            form.save()

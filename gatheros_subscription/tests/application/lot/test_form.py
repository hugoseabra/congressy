from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import six

from gatheros_event.models import Event
from gatheros_subscription.models import Lot
from gatheros_subscription.forms import LotForm


class LotFormTest(TestCase):
    fixtures = [
        '004_category',
        '007_organization',
        '009_place',
        '010_event',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        event = Event.objects.filter(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS
        ).first()

        date_start = datetime.now() + timedelta(days=1)
        date_start = date_start.replace(
            hour=8,
            minute=0,
            second=0,
            microsecond=0
        )
        event.date_start = date_start

        date_end = datetime.now() + timedelta(days=1, hours=6)
        date_end = date_end.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0
        )
        event.date_end = date_end
        event.save()

        return event

    def test_create_edit_lot_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        event = self._get_event()

        date_start = event.date_start - timedelta(days=10)
        date_start = date_start.replace(
            hour=8,
            minute=0,
            second=0,
            microsecond=0
        )

        date_end = event.date_start - timedelta(days=1)
        date_end = date_end.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0
        )

        data = {
            "event": event.pk,
            "name": 'Lot 10',
            "date_start": date_start,
            "date_end": date_end,
            "limit": None,
            "price": None,
            "discount_type": Lot.DISCOUNT_TYPE_PERCENT,
            "discount": None,
            "transfer_tax": False,
            "private": False,
        }

        form = LotForm(data=data, initial={'event': event})
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data.update({
            "event": event.pk,
            "name": 'Lot 10 edited name',
            "limit": 100,
            "price": 25.00,
            "transfer_tax": True,
        })
        form = LotForm(
            instance=form.instance,
            data=data,
            initial={'event': event}
        )
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)


from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import six

from gatheros_event.forms import (
    EventForm,
    EventEditDatesForm,
    EventEditSubscriptionTypeForm,
    EventPublicationForm
)
from gatheros_event.models import Event


class BaseEventFormTest(TestCase):
    fixtures = [
        '007_organization'
    ]

    # noinspection PyMethodMayBeStatic
    def _get_event(self, pk):
        return Event.objects.get(pk=pk)

    # noinspection PyMethodMayBeStatic
    def _get_data(self):
        date_start = datetime.now() + timedelta(days=5)
        date_start = date_start.replace(
            hour=8,
            minute=0,
            second=0,
            microsecond=0
        )

        date_end = datetime.now() + timedelta(days=5, hours=8)
        date_end = date_end.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0
        )

        return {
            "name": 'Event tests',
            "organization": 1,
            "category": 1,
            "subscription_type": Event.SUBSCRIPTION_DISABLED,
            "date_start": date_start,
            "date_end": date_end,
            "subscription_offline": False,
            "published": False,
        }

    def get_main_form(self, instance=None, data=None):
        if not data:
            data = self._get_data()

        return EventForm(instance=instance, data=data)


class EventFormTest(BaseEventFormTest):
    def test_create_edit_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        data = self._get_data()

        form = self.get_main_form()
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data.update({
            'name': 'Event - another name',
            'category': 2
        })

        form = self.get_main_form(instance=form.instance, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)


class EventDatesFormTest(BaseEventFormTest):
    def test_dates_edition_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        data = self._get_data()

        form = self.get_main_form()
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data = {
            'date_start': form.instance.date_start + timedelta(hours=4),
            'date_end': form.instance.date_end + timedelta(hours=4)
        }

        form = EventEditDatesForm(instance=form.instance, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)


class EventSubscriptionTypeFormTest(BaseEventFormTest):
    def test_subscription_type_edition_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        data = self._get_data()

        form = self.get_main_form()
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data = {
            'subscription_type': Event.SUBSCRIPTION_SIMPLE,
            'subscription_offline': True,
        }

        form = EventEditSubscriptionTypeForm(instance=form.instance, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)


class EventPublicationFormTest(BaseEventFormTest):
    def test_publication_edition_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        data = self._get_data()

        form = self.get_main_form()
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data = {
            'published': True,
        }

        form = EventPublicationForm(instance=form.instance, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

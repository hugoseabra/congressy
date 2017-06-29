import json
from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import six

from gatheros_event.models import Event
from gatheros_subscription.forms import (
    SubscriptionAttendanceForm,
    SubscriptionForm,
)
from gatheros_subscription.models import Answer, Subscription


class SubscriptionFormTest(TestCase):
    """ Testa formulário de inscrição. """

    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
        '005_field_option',
        '006_lot',
        '007_subscription',
        '008_answer',
    ]

    def setUp(self):
        self.event = Event.objects.get(slug='django-muito-alem-do-python')
        self.event.date_start = datetime.now() + timedelta(days=2)
        self.event.date_end = datetime.now() + timedelta(days=2, hours=8)
        self.event.save()

        self.lot = self.event.lots.first()
        self.lot.date_end = datetime.now() + timedelta(days=1)
        self.lot.save()

        self.data = {
            'lot': self.lot.pk,
            'name': 'João das Coves',
            'gender': 'M',
            'phone': '62999999999',
            'city': 5413,
        }

        self.data.update({
            "tem-conhecimento-de-logica-de-programacao": True,
            "o-que-pode-contar-da-sua-historia": "Uma história do início...",
            "qual-destas-linguagens-voce-mais-ouve-falar": "php",
            "quais-destas-linguagens-voce-conhece": [
                "java",
                "php",
                "javascript"
            ],
        })

    def test_form_without_lot_field(self):
        """ Testa se formulário não está renderizado com campo de lote. """

        gatheros_form = self.event.form
        form = SubscriptionForm(form=gatheros_form)
        content = form.as_ul()

        self.assertIn(
            '<input type="hidden" name="lot"',
            content
        )

    def test_form_show_lot_list(self):
        """ Testa se formulário está renderizado com campo de lote. """

        gatheros_form = self.event.form
        form = SubscriptionForm(form=gatheros_form, hide_lot=False)
        content = form.as_ul()

        self.assertIn('<select name="lot" ', content)

    def test_add_new_person(self):
        """ Testa adição de nova inscrição. """

        gatheros_form = self.event.form

        form = SubscriptionForm(form=gatheros_form, data=self.data)
        valid = form.is_valid()

        if not valid:
            print(form.errors)

        self.assertTrue(valid)

        subscription = form.save()
        person = subscription.person

        for field_name, answer in six.iteritems(subscription.form_data):
            data_value = self.data.get(field_name)

            if not data_value:
                continue

            if not isinstance(answer, Answer):
                value = getattr(person, field_name)

                if field_name == 'city':
                    value = value.pk

                self.assertEqual(value, data_value)

            else:
                value = json.loads(answer.value)
                value = value.get('value')

                if isinstance(value, list):
                    value.sort()
                    data_value.sort()
                    self.assertListEqual(value, data_value)
                    continue

                self.assertEqual(value, data_value)

    def test_add_subscription_existing_person(self):
        """ Testa nova inscrição com usuário de pessoa já existente. """

        other_sub = Subscription.objects.filter(
            person__user__isnull=False
        ).exclude(event=self.event).first()

        person = other_sub.person
        self.data.update({
            'name': person.name + ' edited',
            'gender': 'F',
            'phone': '62988888888',
            'city': 5413,
            'user': person.user.pk
        })

        gatheros_form = self.event.form
        form = SubscriptionForm(form=gatheros_form, data=self.data)
        valid = form.is_valid()

        if not valid:
            print(form.errors)

        self.assertTrue(valid)

        saved_sub = form.save()
        saved_sub_person = saved_sub.person

        self.assertEqual(person, saved_sub_person)

        for field_name, answer in six.iteritems(saved_sub.form_data):
            data_value = self.data.get(field_name)

            if not data_value:
                continue

            if not isinstance(answer, Answer):
                value = getattr(saved_sub_person, field_name)

                if field_name == 'city':
                    value = value.pk

                self.assertEqual(value, data_value)

            else:
                value = json.loads(answer.value)
                value = value.get('value')

                if isinstance(value, list):
                    value.sort()
                    data_value.sort()
                    self.assertListEqual(value, data_value)
                    continue

                self.assertEqual(value, data_value)

    def test_edit(self):
        """ Testa edição de inscriçõa. """
        sub = self.event.subscriptions.first()

        person = sub.person
        self.data.update({
            'name': person.name + ' edited',
            'gender': 'F',
            'phone': '62988888888',
            'city': 5413,
            'user': person.user.pk
        })

        gatheros_form = self.event.form
        form = SubscriptionForm(
            form=gatheros_form,
            data=self.data,
            instance=sub
        )
        valid = form.is_valid()

        if not valid:
            print(form.errors)

        self.assertTrue(valid)

        saved_sub = form.save()
        saved_sub_person = saved_sub.person

        self.assertEqual(sub.person, person)

        for field_name, answer in six.iteritems(saved_sub.form_data):
            data_value = self.data.get(field_name)

            if not data_value:
                continue

            if not isinstance(answer, Answer):
                value = getattr(saved_sub_person, field_name)

                if field_name == 'city':
                    value = value.pk

                self.assertEqual(value, data_value)

            else:
                value = json.loads(answer.value)
                value = value.get('value')

                if isinstance(value, list):
                    value.sort()
                    data_value.sort()
                    self.assertListEqual(value, data_value)
                    continue

                self.assertEqual(value, data_value)


class SubscriptionAttendanceFormTest(TestCase):
    """ Testa formulário de credenciamento. """

    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '006_lot',
        '007_subscription',
    ]

    def setUp(self):
        self.subscription = Subscription.objects.first()

    def test_register_attendance(self):
        """ Testa registro de credenciamento de inscrição. """
        self.subscription.attended = False
        self.subscription.attended_on = None
        self.subscription.save()

        form = SubscriptionAttendanceForm(instance=self.subscription)
        form.attended(True)

        sub = Subscription.objects.get(pk=self.subscription.pk)

        self.assertTrue(sub.attended)
        self.assertIsNotNone(sub.attended_on)

    def test_unregister_attendance(self):
        """ Testa cancalmento de credenciamento de inscrição. """
        self.subscription.attended = True
        self.subscription.attended_on = datetime.now()
        self.subscription.save()

        form = SubscriptionAttendanceForm(instance=self.subscription)
        form.attended(False)

        sub = Subscription.objects.get(pk=self.subscription.pk)

        self.assertFalse(sub.attended)
        self.assertIsNone(sub.attended_on)

from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Event
from gatheros_subscription.models import Subscription


class SubscriptionAttendanceSearchViewTest(TestCase):
    """ Testa formulário de inscrição. """

    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
        '005_field_option',
        '007_lot',
        '008_subscription',
    ]

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.event = Event.objects.get(slug='django-muito-alem-do-python')

    def _get_url(self, event=None):
        if not event:
            event = self.event

        return reverse(
            'subscription:subscription-attendance-search',
            kwargs={'event_pk': event.pk}
        )

    def _login(self):
        self.client.force_login(self.user)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_search_by_name(self):
        """ Testa busca de inscrições por nome. """
        self._login()

        def search_by_name(value):
            search_value = value
            subs = self.event.subscriptions.filter(
                person__name__icontains=search_value.strip(),
            ).filter(
                completed=True
            ).exclude(status=Subscription.CANCELED_STATUS)

            data = {
                'search_by': 'name',
                'value': search_value.strip(),
            }

            response = self.client.post(self._get_url(), data=data)

            for sub in subs:
                self.assertContains(response, sub.person.name)

        for subscription in self.event.subscriptions.all():
            name = subscription.person.name[0:4]
            search_by_name(name)
            search_by_name(name)

    def test_search_by_email(self):
        """ Testa busca de inscrições por email. """
        self._login()

        def search_by_email(value):
            search_value = value
            try:
                sub = self.event.subscriptions.get(
                    person__email=search_value.strip()
                )
            except Subscription.DoesNotExist:
                sub = None

            data = {
                'search_by': 'email',
                'value': search_value.strip(),
            }

            response = self.client.post(self._get_url(), data=data)
            self.assertContains(response, sub.person.name)

        for subscription in self.event.subscriptions.all():
            email = subscription.person.email
            if email:
                search_by_email(email)

    def test_search_by_code(self):
        """ Testa busca de inscrições por código de inscrição. """
        self._login()

        def search_by_code(value):
            search_value = value
            try:
                sub = self.event.subscriptions.get(code=search_value.strip())
            except Subscription.DoesNotExist:
                sub = None

            data = {
                'search_by': 'code',
                'value': search_value.strip(),
            }

            response = self.client.post(self._get_url(), data=data)
            self.assertContains(response, sub.person.name)

        for subscription in self.event.subscriptions.all():
            search_by_code(subscription.code)

    def test_register_attendance(self):
        """ Testa registro de credenciamento de inscrição. """
        subscription = self.event.subscriptions.first()
        subscription.attended = False
        subscription.attended_on = None
        subscription.save()

        data = {
            'action': 'register'
        }

        url = reverse(
            'subscription:subscription-attendance',
            kwargs={'event_pk': self.event.pk, 'pk': subscription.pk}
        )

        self._login()
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            'Credenciamento de `{}` registrado com sucesso'.format(
                subscription.person.name
            )
        )

        subscription = Subscription.objects.get(pk=subscription.pk)
        self.assertTrue(subscription.attended)
        self.assertIsNotNone(subscription.attended_on)

    def test_unregister_attendance(self):
        """ Testa cancalmento de credenciamento de inscrição. """
        subscription = self.event.subscriptions.first()
        subscription.attended = True
        subscription.attended_on = datetime.now()
        subscription.save()

        data = {
            'action': 'unregister'
        }

        url = reverse(
            'subscription:subscription-attendance',
            kwargs={'event_pk': self.event.pk, 'pk': subscription.pk}
        )

        self._login()
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            'Cancelamento de credenciamento de `{}` registrado com'
            ' sucesso'.format(subscription.person.name)
        )

        subscription = Subscription.objects.get(pk=subscription.pk)
        self.assertFalse(subscription.attended)
        self.assertIsNone(subscription.attended_on)

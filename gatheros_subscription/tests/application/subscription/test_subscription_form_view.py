from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Event
from gatheros_subscription.models import Subscription


class SubscriptionFormViewTest(TestCase):
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
        '006_lot',
        '007_subscription',
        '008_answer',
    ]

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')

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
            'email': 'Joao@coves.com.br',
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

    def _login(self):
        self.client.force_login(self.user)

    def test_add_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        url = reverse('subscription:subscription-add', kwargs={
            'event_pk': self.event.pk,
        })
        response = self.client.get(url, follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_edit_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        sub = Subscription.objects.filter(event=self.event).first()
        url = reverse('subscription:subscription-edit', kwargs={
            'event_pk': self.event.pk,
            'pk': sub.pk
        })
        response = self.client.get(url, follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_delete_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        sub = Subscription.objects.filter(event=self.event).first()
        url = reverse('subscription:subscription-delete', kwargs={
            'event_pk': self.event.pk,
            'pk': sub.pk
        })
        response = self.client.get(url, follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_add_200_logged(self):
        """ 200 quando logado. """
        self._login()
        url = reverse('subscription:subscription-add', kwargs={
            'event_pk': self.event.pk,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_200_logged(self):
        """ 200 quando logado. """
        sub = Subscription.objects.filter(event=self.event).first()
        url = reverse('subscription:subscription-edit', kwargs={
            'event_pk': self.event.pk,
            'pk': sub .pk
        })

        self._login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_200_logged(self):
        """ 200 quando logado. """
        sub = Subscription.objects.filter(event=self.event).first()
        url = reverse('subscription:subscription-delete', kwargs={
            'event_pk': self.event.pk,
            'pk': sub .pk
        })

        self._login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_new_person(self):
        """ Testa adição de nova inscrição. """

        url = reverse('subscription:subscription-add', kwargs={
            'event_pk': self.event.pk,
        })

        self._login()
        response = self.client.post(url, self.data, follow=True)
        self.assertContains(response, 'Pré-inscrição criada com sucesso')

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

        url = reverse('subscription:subscription-add', kwargs={
            'event_pk': self.event.pk,
        })

        self._login()
        response = self.client.post(url, self.data, follow=True)
        self.assertContains(response, 'Pré-inscrição criada com sucesso')

    def test_add_expired_lot(self):
        """ Testa inscrição em lote expirado. """

        self.lot = self.event.lots.first()
        self.lot.date_end = datetime.now() - timedelta(days=1, hours=3)
        self.lot.date_end = datetime.now() - timedelta(days=1)
        self.lot.save()

        self._login()
        url = reverse('subscription:subscription-add', kwargs={
            'event_pk': self.event.pk,
        })
        response = self.client.post(url, self.data, follow=True)
        self.assertContains(response, 'Lote(s) não disponível(is)')

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

        url = reverse('subscription:subscription-edit', kwargs={
            'event_pk': self.event.pk,
            'pk': sub.pk
        })

        self._login()
        response = self.client.post(url, self.data, follow=True)
        self.assertContains(response, 'Pré-inscrição alterada com sucesso')

    def test_delete(self):
        """ Testa exclusão de inscrição. """

        sub = self.event.subscriptions.first()

        url = reverse('subscription:subscription-delete', kwargs={
            'event_pk': self.event.pk,
            'pk': sub.pk
        })
        self._login()
        response = self.client.post(url, self.data, follow=True)
        self.assertContains(response, 'Pré-inscrição excluída com sucesso')

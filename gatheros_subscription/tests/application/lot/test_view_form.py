from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import Count
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from gatheros_event.helpers import account
from gatheros_event.models import Event, Member, Organization
from gatheros_subscription.models import Lot


class MockSession(SessionStore):
    def __init__(self):
        super(MockSession, self).__init__()


class MockRequest(HttpRequest):
    def __init__(self, user, session=None):
        self.user = user
        if not session:
            session = MockSession()

        self.session = session
        super(MockRequest, self).__init__()


class LotAddTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        self.url = reverse_lazy('event:event-add')
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        self.client.force_login(self.user)
        self._switch_context()

    # noinspection PyMethodMayBeStatic
    def _get_url(self, event_pk):
        return reverse(
            'subscription:lot-add',
            kwargs={'event_pk': event_pk}
        )

    def _get_active_organization(self):
        request = MockRequest(self.user, self.client.session)
        return account.get_organization(request)

    def _switch_context(self, group=Member.ADMIN):
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            members__group=group
        ).first()
        url = reverse('event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def _get_event(self, pk=None):
        if not pk:
            organization = self._get_active_organization()
            event = organization.events.filter(
                subscription_type=Event.SUBSCRIPTION_BY_LOTS
            ).first()
        else:
            event = Event.objects.get(pk=pk)

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

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(1), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next='
        redirect_url += reverse('event:event-panel', kwargs={'pk': 1})
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        event = self._get_event()
        response = self.client.get(self._get_url(event.pk))
        self.assertEqual(response.status_code, 200)

    def test_add(self):
        self._login()
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
            "limit": '',
            "price": '',
            "discount_type": Lot.DISCOUNT_TYPE_PERCENT,
            "discount": '',
            "transfer_tax": False,
            "private": False,
        }

        response = self.client.post(self._get_url(event.pk), data, follow=True)
        self.assertContains(response, 'Lote criado com sucesso.')

    def test_cannot_add_lot(self):
        self._login()
        organization = self._get_active_organization()
        pks = [event.pk for event in organization.events.all()]
        event = Event.objects.exclude(pk__in=pks).filter(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS
        ).first()

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
            "limit": '',
            "price": '',
            "discount_type": Lot.DISCOUNT_TYPE_PERCENT,
            "discount": '',
            "transfer_tax": False,
            "private": False,
        }

        response = self.client.post(self._get_url(event.pk), data, follow=True)
        self.assertContains(
            response,
            "Você não pode adicionar lote neste evento."
        )


class LotEditTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '007_lot',
    ]

    def setUp(self):
        self.url = reverse_lazy('event:event-add')
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        self.client.force_login(self.user)
        self._switch_context()

    # noinspection PyMethodMayBeStatic
    def _get_url(self, event_pk, pk):
        return reverse(
            'subscription:lot-edit',
            kwargs={'event_pk': event_pk, 'lot_pk': pk}
        )

    def _get_active_organization(self):
        request = MockRequest(self.user, self.client.session)
        return account.get_organization(request)

    def _switch_context(self, group=Member.ADMIN):
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            members__group=group
        ).first()
        url = reverse('event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def _get_event(self, pk=None):
        if not pk:
            organization = self._get_active_organization()
            event = organization.events.annotate(num=Count('lots')).filter(
                subscription_type=Event.SUBSCRIPTION_BY_LOTS,
                num__gt=0
            ).first()
        else:
            event = Event.objects.get(pk=pk)

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

    def _get_lot(self, pk=None):
        if not pk:
            event = self._get_event()
            return event.lots.first()

        return Lot.objects.get(pk=pk)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        lot = self._get_lot(1)
        url = self._get_url(lot.event.pk, lot.pk)
        response = self.client.get(url, follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next='
        redirect_url += reverse(
            'event:event-panel',
            kwargs={'pk'> lot.event.pk}
        )
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        lot = self._get_lot()
        result = self.client.get(self._get_url(lot.event.pk, lot.pk))
        self.assertEqual(result.status_code, 200)

    def test_edit(self):
        self._login()
        lot = self._get_lot()

        data = {
            'event': lot.event.pk,
            'name': lot.name,
            'date_start': lot.date_start,
            'date_end': lot.date_end,
            'limit': '' if not lot.limit else lot.limit,
            'price': '' if not lot.price else lot.price,
            'discount_type': lot.discount_type,
            'discount': '' if not lot.discount else lot.discount,
            'transfer_tax': '' if not lot.transfer_tax else lot.transfer_tax,
            'private': lot.private
        }

        data.update({
            'name': 'Lot 200 edited',
            'limit': 100,
            'price': 25.00,
            'private': True,
        })

        # Valores alterados não são iguais aos persistidos
        self.assertNotEqual(lot.name, data['name'])
        self.assertNotEqual(lot.limit, data['limit'])
        self.assertNotEqual(lot.price, data['price'])
        self.assertNotEqual(lot.private, data['private'])

        response = self.client.post(
            self._get_url(lot.event.pk, lot.pk),
            data,
            follow=True
        )

        self.assertContains(
            response,
            'Lote alterado com sucesso.'
        )

        # Valores foram alterados na persistência
        lot = self._get_lot(pk=lot.pk)
        self.assertEqual(lot.name, data['name'])
        self.assertEqual(lot.limit, data['limit'])
        self.assertEqual(lot.price, data['price'])
        self.assertEqual(lot.private, data['private'])

    def test_cannot_edit_lot(self):
        self._login()
        organization = self._get_active_organization()
        pks = [event.pk for event in organization.events.all()]
        lot = Lot.objects.exclude(event_id__in=pks).first()

        data = {
            'event': lot.event.pk,
            'name': lot.name,
            'date_start': lot.date_start,
            'date_end': lot.date_end,
            'limit': '' if not lot.limit else lot.limit,
            'price': '' if not lot.price else lot.price,
            'discount_type': lot.discount_type,
            'discount': '' if not lot.discount else lot.discount,
            'transfer_tax': '' if not lot.transfer_tax else lot.transfer_tax,
            'private': lot.private
        }

        data.update({
            'name': 'Lot 200 edited',
            'limit': 100,
            'price': 25.00,
            'private': True,
        })

        # Valores alterados não são iguais aos persistidos
        self.assertNotEqual(lot.name, data['name'])
        self.assertNotEqual(lot.limit, data['limit'])
        self.assertNotEqual(lot.price, data['price'])
        self.assertNotEqual(lot.private, data['private'])

        response = self.client.post(
            self._get_url(lot.event.pk, lot.pk),
            data,
            follow=True
        )

        self.assertContains(
            response,
            "Você não pode editar lote neste evento."
        )


class LotDeleteTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '007_lot',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        self.client.force_login(self.user)
        self._switch_context()

    # noinspection PyMethodMayBeStatic
    def _get_url(self, event_pk, pk):
        return reverse(
            'subscription:lot-delete',
            kwargs={'event_pk': event_pk, 'lot_pk': pk}
        )

    def _get_active_organization(self):
        return account.get_organization(self.client.request().wsgi_request)

    def _switch_context(self, group=Member.ADMIN):
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            members__group=group
        ).first()
        url = reverse('event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def _get_event(self, pk=None):
        if not pk:
            organization = self._get_active_organization()
            event = organization.events.annotate(num=Count('lots')).filter(
                subscription_type=Event.SUBSCRIPTION_BY_LOTS,
                num__gt=0
            ).first()
        else:
            event = Event.objects.get(pk=pk)

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

    def _get_lot(self, pk=None):
        if not pk:
            event = self._get_event()
            return event.lots.first()

        return Lot.objects.get(pk=pk)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        lot = self._get_lot(1)
        url = self._get_url(lot.event.pk, lot.pk)
        response = self.client.get(url, follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next='
        redirect_url += reverse(
            'event:event-panel',
            kwargs={'pk': lot.event.pk}
        )
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        lot = self._get_lot()
        result = self.client.get(self._get_url(lot.event.pk, lot.pk))
        self.assertEqual(result.status_code, 200)

    def test_delete(self):
        self._login()
        lot = self._get_lot()

        response = self.client.post(
            self._get_url(lot.event.pk, lot.pk),
            follow=True
        )

        self.assertContains(
            response,
            'Lote excluído com sucesso'
        )

        # Valores foram alterados na persistência
        with self.assertRaises(Lot.DoesNotExist):
            self._get_lot(pk=lot.pk)

    def test_cannot_edit_lot(self):
        self._login()
        organization = self._get_active_organization()
        pks = [event.pk for event in organization.events.all()]
        lot = Lot.objects.exclude(event_id__in=pks).first()

        response = self.client.post(
            self._get_url(lot.event.pk, lot.pk),
            follow=True
        )

        self.assertContains(
            response,
            "Você não pode excluir lote neste evento"
        )

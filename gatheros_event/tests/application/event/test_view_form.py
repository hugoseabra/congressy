""" Testes de aplicação com `Event` - Formulários pela view. """
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from gatheros_event.helpers import account
from gatheros_event.models import Event, Member, Organization


class EventAddViewTest(TestCase):
    """ Testa view de adicionar evento. """

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
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_active_organization(self):
        """ Resgata organização ativa. """
        request = self.client.request().wsgi_request
        return account.get_organization(request)

    def _switch_context(self, group=Member.ADMIN):
        """ Muda para outra organização do contexto do usuário. """
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            internal=False,
            members__group=group
        ).first()
        url = reverse('event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self.url, follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_status_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_add_event(self):
        """ Testa adição de evento. """
        self._login()
        org = self._get_active_organization()
        data = {
            'organization': org.pk,
            'category': 1,
            'name': 'Event teste nah',
            'date_start': datetime.now() + timedelta(days=5),
            'date_end': datetime.now() + timedelta(days=5, hours=6),
            'subscription_type': Event.SUBSCRIPTION_DISABLED,
            'subscription_offline': False,
            'published': False
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, 'Evento criado com sucesso.')

    def test_cannot_add_event(self):
        """ Testa restrição de adição de evento. """
        self._login()
        self._switch_context(group=Member.HELPER)
        org = self._get_active_organization()

        data = {
            'organization': org.pk,
            'category': 1,
            'name': 'Event teste nah',
            'date_start': datetime.now() + timedelta(days=5),
            'date_end': datetime.now() + timedelta(days=5, hours=6),
            'subscription_type': Event.SUBSCRIPTION_DISABLED,
            'subscription_offline': False,
            'published': False
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertContains(
            response,
            'Você não pode inserir um evento nesta organização'
        )


class EventEditViewTest(TestCase):
    """ Testes de view para editar evento. """
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '003_occupation',
        '004_category',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_active_organization(self):
        """ Recupera organização ativa do contexto do usuário. """
        request = self.client.request().wsgi_request
        return account.get_organization(request)

    # noinspection PyMethodMayBeStatic
    def _get_url(self, pk):
        """ Resgata URL. """
        return reverse('event:event-edit', kwargs={'pk': pk})

    def _get_event(self, pk=None):
        """ Resgata instânica de Event. """
        if not pk:
            organization = self._get_active_organization()
            return organization.events.first()

        return Event.objects.get(pk=pk)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(pk=1), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_status_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        event = self._get_event()
        result = self.client.get(self._get_url(pk=event.pk))
        self.assertEqual(result.status_code, 200)

    def test_edit_event(self):
        """ Testa edição de evento. """
        self._login()
        event = self._get_event()

        data = model_to_dict(event, fields=(
            'organization',
            'category',
            'name',
            'date_start',
            'date_end',
            'subscription_type',
            'subscription_offline',
            'published'
        ))

        data.update({
            'category': 4,
            'name': 'Event edited',
        })

        # Valores alterados não são iguais aos persistidos
        self.assertNotEqual(event.category_id, data['category'])
        self.assertNotEqual(event.name, data['name'])

        response = self.client.post(
            self._get_url(pk=event.pk),
            data,
            follow=True
        )

        self.assertContains(
            response,
            'Evento alterado com sucesso.'
        )

        # Valores foram alterados na persistência
        event = self._get_event(pk=event.pk)
        self.assertEqual(event.category_id, data['category'])
        self.assertEqual(event.name, data['name'])

    def test_cannot_edit_event(self):
        """ Testa restrição de edição de evento. """
        self._login()
        organization = self._get_active_organization()
        pks = [event.pk for event in organization.events.all()]
        event = Event.objects.exclude(pk__in=pks).first()

        data = model_to_dict(event, fields=(
            'organization',
            'category',
            'name',
            'date_start',
            'date_end',
            'subscription_type',
            'subscription_offline',
            'published'
        ))
        response = self.client.post(
            self._get_url(pk=event.pk),
            data,
            follow=True
        )
        self.assertContains(
            response,
            'Você não tem permissão para editar este evento'
        )


class EventDatesEditViewTest(TestCase):
    """ Testes de views para editar datas de evento. """
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
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_active_organization(self):
        request = self.client.request().wsgi_request
        return account.get_organization(request)

    # noinspection PyMethodMayBeStatic
    def _get_url(self, pk):
        """ Resgata URL. """
        return reverse('event:event-edit-dates', kwargs={'pk': pk})

    def _get_event(self, pk=None):
        """ Resgata instânica de Event. """
        if not pk:
            organization = self._get_active_organization()
            event = organization.events.first()
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
        response = self.client.get(self._get_url(pk=1), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_status_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        event = self._get_event()
        result = self.client.get(self._get_url(pk=event.pk))
        self.assertEqual(result.status_code, 200)

    def test_edit_event(self):
        """ Testa edição de datas de evento. """
        self._login()
        event = self._get_event()

        data = model_to_dict(event, fields=(
            'date_start',
            'date_end',
        ))

        data.update({
            'date_start': event.date_start + timedelta(days=2),
            'date_end': event.date_end + timedelta(days=2),
        })

        response = self.client.post(
            self._get_url(pk=event.pk),
            data,
            follow=True
        )

        self.assertContains(
            response,
            'Datas alteradas com sucesso.'
        )

        # Valores foram alterados na persistência
        event = self._get_event(pk=event.pk)
        self.assertEqual(
            event.date_start.strftime('%Hh%M'),
            data['date_start'].strftime('%Hh%M')
        )
        self.assertEqual(
            event.date_end.strftime('%Hh%M'),
            data['date_end'].strftime('%Hh%M')
        )

    def test_cannot_edit_event(self):
        """ Testa restrição de edição de datas de evento. """
        self._login()
        organization = self._get_active_organization()
        pks = [event.pk for event in organization.events.all()]
        event = Event.objects.exclude(pk__in=pks).first()

        data = model_to_dict(event, fields=(
            'date_start',
            'date_end',
        ))

        data.update({
            'date_start': event.date_start + timedelta(days=2),
            'date_end': event.date_end + timedelta(days=2),
        })

        response = self.client.post(
            self._get_url(pk=event.pk),
            data,
            follow=True
        )

        self.assertContains(
            response,
            'Você não tem permissão para editar este evento'
        )


class EventSubscriptionTypeEditViewTest(TestCase):
    """ Testes de view para editar tipo de inscrição de evento. """
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '003_occupation',
        '004_category',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_active_organization(self):
        request = self.client.request().wsgi_request
        return account.get_organization(request)

    # noinspection PyMethodMayBeStatic
    def _get_url(self, pk):
        return reverse(
            'event:event-edit-subscription_type',
            kwargs={'pk': pk}
        )

    def _get_event(self, pk=None):
        if not pk:
            organization = self._get_active_organization()
            event = organization.events.exclude(
                subscription_type=Event.SUBSCRIPTION_SIMPLE
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
        response = self.client.get(self._get_url(pk=1), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_status_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        event = self._get_event()
        result = self.client.get(self._get_url(pk=event.pk))
        self.assertEqual(result.status_code, 200)

    def test_edit_event(self):
        """ Testa edição de tipo de inscrição de evento. """
        self._login()
        event = self._get_event()

        data = model_to_dict(event, fields=(
            'subscription_type',
            'subscription_offline',
        ))

        data.update({
            'subscription_type': Event.SUBSCRIPTION_SIMPLE,
            'subscription_offline': False,
        })
        self.assertNotEqual(event.subscription_type, data['subscription_type'])
        self.assertNotEqual(
            event.subscription_offline,
            data['subscription_offline']
        )

        response = self.client.post(
            self._get_url(pk=event.pk),
            data,
            follow=True
        )

        self.assertContains(
            response,
            'Tipo de inscrição alterada com sucesso.'
        )

        # Valores foram alterados na persistência
        event = self._get_event(pk=event.pk)
        self.assertEqual(event.subscription_type, data['subscription_type'])
        self.assertEqual(
            event.subscription_offline,
            data['subscription_offline']
        )

    def test_cannot_edit_event(self):
        """ Testa restrição de edição de tipo de inscrição de evento. """
        self._login()
        organization = self._get_active_organization()
        pks = [event.pk for event in organization.events.all()]
        event = Event.objects.exclude(pk__in=pks).first()

        data = model_to_dict(event, fields=(
            'subscription_type',
            'subscription_offline',
        ))

        response = self.client.post(
            self._get_url(pk=event.pk),
            data,
            follow=True
        )

        self.assertContains(
            response,
            'Você não tem permissão para editar este evento'
        )


class EventPublicationEditViewTest(TestCase):
    """ Testes de view para publicar/despublicar evento. """
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '003_occupation',
        '004_category',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_active_organization(self):
        request = self.client.request().wsgi_request
        return account.get_organization(request)

    # noinspection PyMethodMayBeStatic
    def _get_url(self, pk):
        return reverse(
            'event:event-edit-publication',
            kwargs={'pk': pk}
        )

    def _get_event(self, pk=None):
        if not pk:
            organization = self._get_active_organization()
            return organization.events.first()

        return Event.objects.get(pk=pk)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(pk=1), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_status_is_405(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        event = self._get_event()
        result = self.client.get(self._get_url(pk=event.pk))
        self.assertEqual(result.status_code, 405)

    def test_edit_event(self):
        """ Testa edição de publicação de evento. """
        self._login()
        event = self._get_event()

        data = model_to_dict(event, fields=('published',))

        data.update({'published': not event.published})

        self.client.post(
            self._get_url(pk=event.pk),
            data,
            follow=True
        )

        # Valores foram alterados na persistência
        event = self._get_event(pk=event.pk)
        self.assertEqual(event.published, data['published'])

    def test_cannot_edit_event(self):
        """ Testa restrição de edição de publicação de evento. """
        self._login()
        organization = self._get_active_organization()
        pks = [event.pk for event in organization.events.all()]
        event = Event.objects.exclude(pk__in=pks).first()

        data = model_to_dict(event, fields=(
            'subscription_type',
            'subscription_offline',
        ))

        response = self.client.post(
            self._get_url(pk=event.pk),
            data,
            follow=True
        )

        self.assertContains(
            response,
            'Você não tem permissão para editar este evento'
        )

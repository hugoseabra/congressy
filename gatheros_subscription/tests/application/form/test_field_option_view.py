from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from gatheros_event.models import Event
from gatheros_subscription.models import Field, FieldOption


class FieldOptionViewTest(TestCase):
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '002_form',
        '003_field',
        '004_field_option',
    ]

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.event = Event.objects.get(slug='arte-e-agricultura-urbana')

    def _get_url(self, event=None, field=None):
        if not event:
            event = self.event

        if not field:
            field = event.form.fields.filter(with_options=True).first()

        return reverse('gatheros_subscription:field-options', kwargs={
            'event_pk': event.pk,
            'field_pk': field.pk
        })

    def _login(self):
        self.client.force_login(self.user)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('gatheros_front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_error_no_option_support(self):
        """ Não permite edição de opção sem suporte a opções. """
        self._login()
        field = self.event.form.fields.filter(with_options=False).first()
        response = self.client.get(self._get_url(field=field), follow=True)
        self.assertContains(response, 'Este campo não possui suporte a opções')


class FieldOptionAddViewTest(TestCase):
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '002_form',
        '003_field',
        '004_field_option',
    ]

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.event = Event.objects.get(slug='arte-e-agricultura-urbana')

    def _get_url(self):
        return reverse('gatheros_subscription:field-option-add')

    def _login(self):
        self.client.force_login(self.user)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('gatheros_front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_get_405(self):
        """ 405 quando acessado por GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 405)

    def test_add(self):
        """ Testa adição de opção. """
        self._login()
        field = self.event.form.fields.filter(with_options=True).first()
        num = field.options.count()

        data = {
            'field_pk': field.pk,
            'name': 'New option 555'
        }

        self.client.post(self._get_url(), data=data, follow=True)
        option = FieldOption.objects.get(name=data['name'], field=field)
        self.assertIsInstance(option, FieldOption)

        field = Field.objects.get(pk=field.pk)
        self.assertEqual(field.options.count(), num + 1)


class FieldOptionEditViewTest(TestCase):
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '002_form',
        '003_field',
        '004_field_option',
    ]

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.event = Event.objects.get(
            slug='arte-e-agricultura-urbana')

    def _get_url(self, field_option=None):
        if not field_option:
            field = self.event.form.fields.filter(with_options=True).first()
            field_option = field.options.first()

        return reverse('gatheros_subscription:field-option-edit', kwargs={
            'pk': field_option.pk
        })

    def _login(self):
        self.client.force_login(self.user)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('gatheros_front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_get_405(self):
        """ 405 quando acessado por GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 405)

    def test_edit(self):
        """ Testa edição. """
        self._login()
        field = self.event.form.fields.filter(with_options=True).first()
        field_option = field.options.first()

        data = {'name': field.name + ' edited'}

        self.client.post(
            self._get_url(field_option=field_option),
            data=data,
            follow=True
        )

        field_option = FieldOption.objects.get(pk=field_option.pk)
        self.assertEqual(field_option.name, data['name'])


class FieldOptionDeleteViewTest(TestCase):
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '002_form',
        '003_field',
        '004_field_option',
    ]

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.event = Event.objects.get(
            slug='arte-e-agricultura-urbana')

    def _get_url(self, field_option=None):
        if not field_option:
            field = self.event.form.fields.filter(with_options=True).first()
            field_option = field.options.first()

        return reverse('gatheros_subscription:field-option-delete', kwargs={
            'pk': field_option.pk
        })

    def _login(self):
        self.client.force_login(self.user)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('gatheros_front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_get_405(self):
        """ 405 quando acessado por GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        self._login()
        field = self.event.form.fields.filter(with_options=True).first()
        field_option = field.options.first()

        self.client.post(
            self._get_url(field_option=field_option),
            follow=True
        )

        with self.assertRaises(FieldOption.DoesNotExist):
            FieldOption.objects.get(pk=field_option.pk)

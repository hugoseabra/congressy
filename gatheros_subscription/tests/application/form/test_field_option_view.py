""" Testes de aplicação `Field` - views. """
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Organization
from gatheros_subscription.models import Field, FieldOption

FIXTURES = [
    '005_user',
    '006_person',
    '007_organization',
    '008_member',
    '009_place',
    '010_event',
    '003_form',
    '004_field',
    '005_field_option',
]


class FieldOptionViewTest(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.field = self.organization.fields.filter(
            form_default_field=False,
            with_options=True
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self, field=None):
        if not field:
            field = self.field

        return reverse('subscription:field-options', kwargs={
            'field_pk': field.pk
        })

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

    def test_not_org_member(self):
        """
        Não permite edição de opção de campo cuja organização o usuário não é
        membro.
        """
        user = User.objects.get(email='lucianasilva@gmail.com')
        self.client.force_login(user)

        field = self.organization.fields.filter(
            form_default_field=False
        ).first()

        response = self.client.get(self._get_url(field=field), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_error_no_option_support(self):
        """ Não permite edição de opção sem suporte a opções. """
        self._login()
        field = self.organization.fields.filter(with_options=False).first()
        response = self.client.get(self._get_url(field=field), follow=True)
        self.assertContains(response, 'Este campo não possui suporte a opções')

    def test_error_default_field(self):
        """ Não permite edição de opção de campo padrão. """
        self._login()

        # Sexo é padrão
        field = self.organization.fields.get(name='gender')

        response = self.client.get(self._get_url(field=field), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')


class FieldOptionAddViewTest(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.field = self.organization.fields.filter(
            form_default_field=False,
            with_options=True
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    # noinspection PyMethodMayBeStatic
    def _get_url(self):
        return reverse('subscription:field-option-add')

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_get_forbidden(self):
        """ 405 quando acessado por GET. """
        self._login()
        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_not_org_member(self):
        """
        Não permite adição de opção de campo cuja organização o usuário não é
        membro.
        """
        user = User.objects.get(email='lucianasilva@gmail.com')
        self.client.force_login(user)
        data = {'field_pk': self.field.pk}

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_not_org_field(self):
        """
        Não permite adição de opção de campo cuja organização o usuário não é
        membro.
        """
        field = Field.objects.filter(
            form_default_field=False,
            with_options=True
        ).exclude(organization=self.organization).first()
        data = {'field_pk': field.pk}

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_add(self):
        """ Testa adição de opção. """
        self._login()
        num = self.field.options.count()

        data = {
            'field_pk': self.field.pk,
            'name': 'New option 555'
        }

        self.client.post(self._get_url(), data=data, follow=True)
        option = FieldOption.objects.get(name=data['name'], field=self.field)
        self.assertIsNotNone(option)
        self.assertEqual(self.field.options.count(), num + 1)


class FieldOptionEditViewTest(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.field = self.organization.fields.filter(
            form_default_field=False,
            with_options=True
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self, field_option=None):
        if not field_option:
            field_option = self.field.options.first()

        return reverse('subscription:field-option-edit', kwargs={
            'pk': field_option.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_get_forbidden(self):
        """ 405 quando acessado por GET. """
        self._login()
        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_not_org_member(self):
        """
        Não permite edição de opção de campo cuja organização o usuário não é
        membro.
        """
        user = User.objects.get(email='lucianasilva@gmail.com')
        self.client.force_login(user)
        data = {'field_pk': self.field.pk}

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_not_org_field(self):
        """
        Não permite edição de opção de campo cuja organização o usuário não é
        membro.
        """
        field = Field.objects.filter(
            form_default_field=False,
            with_options=True
        ).exclude(organization=self.organization).first()
        data = {'field_pk': field.pk}

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_edit(self):
        """ Testa edição. """
        self._login()
        option = self.field.options.first()

        data = {'name': option.name + ' edited'}

        self.client.post(
            self._get_url(field_option=option),
            data=data,
            follow=True
        )

        field_option = FieldOption.objects.get(pk=option.pk)
        self.assertEqual(field_option.name, data['name'])


class FieldOptionDeleteViewTest(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.field = self.organization.fields.filter(
            form_default_field=False,
            with_options=True
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self, field_option=None):
        if not field_option:
            field_option = self.field.options.first()

        return reverse('subscription:field-option-delete', kwargs={
            'pk': field_option.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_get_405(self):
        """ 405 quando acessado por GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 405)

    def test_not_org_member(self):
        """
        Não permite edição de opção de campo cuja organização o usuário não é
        membro.
        """
        user = User.objects.get(email='lucianasilva@gmail.com')
        self.client.force_login(user)
        data = {'field_pk': self.field.pk}

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_not_org_field(self):
        """
        Não permite edição de opção de campo cuja organização o usuário não é
        membro.
        """
        field = Field.objects.filter(
            form_default_field=False,
            with_options=True
        ).exclude(organization=self.organization).first()
        data = {'field_pk': field.pk}

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_delete(self):
        self._login()
        option = self.field.options.first()

        self.client.post(
            self._get_url(field_option=option),
            follow=True
        )

        with self.assertRaises(FieldOption.DoesNotExist):
            FieldOption.objects.get(pk=option.pk)

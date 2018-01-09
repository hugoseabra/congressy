""" Testes de aplicação `Form` - views. """
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Organization
from gatheros_subscription.models import Field, Form

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


class EventFormViewRenderTest(TestCase):
    """ Testes de exibição de configuração de formulário de evento. """
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.event = self.organization.events.first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self):
        return reverse(
            'subscription:event-fields-config',
            kwargs={'event_pk': self.event.pk}
        )

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

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')


class EventFormAddTest(TestCase):
    """ Testes de adição de campos em formulário de evento. """
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.event = self.organization.events.first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self):
        return reverse(
            'subscription:event-field-add',
            kwargs={'event_pk': self.event.pk}
        )

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

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_copy_form(self):
        """
        Testa cópia de formulário de um evento para outro com todos os campos.
        """
        self._login()

        event = self.organization.events.exclude(
            pk=self.event.pk,
            subscription_type=self.event.SUBSCRIPTION_DISABLED
        ).first()

        fields_list = []
        required_fields_list = []
        required_fields = []
        not_required_fields_list = []
        for field in event.form.fields.filter(form_default_field=False):
            fields_list.append(field.name)

            # Inversão
            if not field.required:
                required_fields_list.append('required')
                required_fields.append(field)

            else:
                required_fields_list.append('not-required')
                not_required_fields_list.append(field)

        data = {
            'fields_list': fields_list,
            'requirement_list': required_fields_list,
            'action': 'copy'
        }

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Campos adicionados com sucesso')

        form = Form.objects.get(pk=self.event.form.pk)

        for field in required_fields:
            self.assertTrue(form.is_required(field))

        for field in not_required_fields_list:
            self.assertFalse(form.is_required(field))

    def test_add_existing_field(self):
        """
        Testa adição de campo existente em formulário de um evento.
        """
        self._login()

        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': 'Some strange name',
            'organization': self.organization
        }
        field = Field.objects.create(**data)

        # Obrigatório no formulário
        data = {
            'field_name': field.name,
            'action': 'add_existing',
            'requirement': 'required'
        }

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Campo adicionado com sucesso')

        field = Field.objects.get(pk=field.pk)

        self.assertFalse(field.required)
        self.assertTrue(self.event.form.is_required(field))

        # Não-obrigatório no formulário
        data.update({'requirement': 'not-required'})

        # Campo é obrigatório por padrão
        field.required = True
        field.save()

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Campo adicionado com sucesso')

        field = Field.objects.get(pk=field.pk)
        form = Form.objects.get(pk=self.event.form.pk)

        self.assertTrue(field.required)
        self.assertFalse(form.is_required(field))

    def test_add_new_field(self):
        """
        Testa adição de novo campo.
        """
        self._login()
        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': 'Some strange name',
            'action': 'add',
            'required': True
        }

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Campo adicionado com sucesso')

        field = self.event.form.fields.last()
        self.assertEqual(field.label, data['label'])

        self.assertTrue(field.required)
        self.assertTrue(self.event.form.is_required(field))


class EventFormEditViewTest(TestCase):
    """ Testes de edição de campo de formulário. """
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.event = self.organization.events.first()
        self.field = self.event.form.fields.filter(
            form_default_field=False
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self, field=None):
        if not field:
            field = self.field

        return reverse('subscription:field-edit', kwargs={'pk': field.pk})

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

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_edit_field_restriction(self):
        """ Testa restrição de edição de `Field`. """
        self._login()
        default_field = self.event.form.fields.filter(
            form_default_field=True
        ).first()

        response = self.client.post(self._get_url(default_field), follow=True)
        self.assertContains(response, 'Este campo não pode ser editado')

    def test_edit_field_redirects_back(self):
        """
        A responsabilidade de edição de campo é da view da organização.

        Somente é necessário saber se o retorno de tela volta para as
        configurações de formulário de evento.
        """
        self._login()
        event_fields_config_path = reverse(
            'subscription:event-fields-config',
            kwargs={'event_pk': self.event.pk}
        )

        data = {
            'field_type': Field.FIELD_SELECT,
            'label': self.field.label + ' edited',
            'next_path': event_fields_config_path
        }

        response = self.client.post(self._get_url(), data=data)
        self.assertRedirects(response, event_fields_config_path)


class EventFormRemoveFieldViewTest(TestCase):
    """ Testes de exclusão da relação do campo com o formulário do evento. """
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(
            slug='diego-tolentino')
        self.event = self.organization.events.first()
        self.field = self.event.form.fields.filter(
            form_default_field=False
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self, field=None):
        if not field:
            field = self.field

        return reverse('subscription:event-field-remove', kwargs={
            'event_pk': self.event.pk,
            'pk': field.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_405_logged(self):
        """ 405 quando logado. """
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

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_remove_field(self):
        """ Testa remoção de campo pela view. """
        self._login()

        self.client.post(self._get_url(), follow=True)

        form = Form.objects.get(pk=self.event.form.pk)
        self.assertNotIn(self.field, form.fields.all())


class EventFormManageActivatationViewTest(TestCase):
    """ Testes de ativação/desativação de campo de formulário. """
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(
            slug='diego-tolentino')
        self.event = self.organization.events.first()
        self.field = self.event.form.fields.filter(
            form_default_field=False
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self, field=None):
        if not field:
            field = self.field

        return reverse('subscription:event-manage-activation', kwargs={
            'event_pk': self.event.pk,
            'pk': field.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_405_logged(self):
        """ 405 quando logado. """
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

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_activate_field(self):
        """ Testa ativação de campo pela view. """
        self._login()

        form = self.event.form
        form.deactivate_field(self.field)
        self.assertFalse(form.is_active(self.field))

        data = {'action': 'activate'}

        self.client.post(self._get_url(), data=data, follow=True)

        form = Form.objects.get(pk=form.pk)
        field = Field.objects.get(pk=self.field.pk)
        self.assertTrue(form.is_active(field))

    def test_deactivate_field(self):
        """ Testa desativação de campo pela view. """
        self._login()

        form = self.event.form
        self.assertTrue(form.is_active(self.field))

        data = {'action': 'deactivate'}

        self.client.post(self._get_url(), data=data, follow=True)

        form = Form.objects.get(pk=form.pk)
        field = Field.objects.get(pk=self.field.pk)
        self.assertFalse(form.is_active(field))


class EventFormFieldReorderViewTest(TestCase):
    """ Testes de reordenação de campo de formulário. """
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(
            slug='diego-tolentino')
        self.event = self.organization.events.first()
        self.field = self.event.form.fields.filter(
            form_default_field=False
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self, field=None):
        if not field:
            field = self.field

        return reverse('subscription:event-field-order', kwargs={
            'event_pk': self.event.pk,
            'pk': field.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_405_logged(self):
        """ 405 quando logado. """
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

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_order_up(self):
        """ Testa reordenação para cima. """
        self._login()

        form = self.event.form
        order = form.get_field_order(self.field)
        data = {'up': ''}

        self.client.post(self._get_url(), data=data, follow=True)

        form = Form.objects.get(pk=form.pk)
        field = Field.objects.get(pk=self.field.pk)

        self.assertEqual(form.get_field_order(field), order + 1)

    def test_order_down(self):
        """ Testa reordenação para baixo. """
        self._login()

        form = self.event.form
        order = form.get_field_order(self.field)
        data = {'down': ''}

        self.client.post(self._get_url(), data=data, follow=True)

        form = Form.objects.get(pk=form.pk)
        field = Field.objects.get(pk=self.field.pk)

        self.assertEqual(form.get_field_order(field), order - 1)


class EventFormFieldRequirementViewTest(TestCase):
    """ Testes de gestão de campos obrigatórios no formulário. """
    fixtures = FIXTURES

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.organization = Organization.objects.get(
            slug='diego-tolentino')
        self.event = self.organization.events.first()
        self.field = self.event.form.fields.filter(
            form_default_field=False
        ).first()

    def _login(self):
        self.client.force_login(self.user)

    def _get_url(self, field=None):
        if not field:
            field = self.field

        return reverse('subscription:event-manage-requirement', kwargs={
            'event_pk': self.event.pk,
            'pk': field.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_405_logged(self):
        """ 405 quando logado. """
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

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_set_as_required(self):
        """ Testa definição de um campo no formulário como obrigatório. """
        self._login()

        form = self.event.form
        self.assertFalse(form.is_required(self.field))

        data = {'action': 'required'}

        self.client.post(self._get_url(), data=data, follow=True)

        form = Form.objects.get(pk=form.pk)
        field = Field.objects.get(pk=self.field.pk)

        self.assertTrue(form.is_required(field))

    def test_set_not_required(self):
        """ Testa definição de um campo no formulário como não-obrigatório. """
        self._login()

        required_field = Field.objects.filter(
            required=True,
            form_default_field=False,
            forms__event=self.event.pk
        ).first()
        self.assertTrue(required_field.required)

        data = {'action': 'not-required'}

        self.client.post(self._get_url(required_field), data=data, follow=True)

        form = Form.objects.get(pk=self.event.form.pk)
        field = Field.objects.get(pk=required_field.pk)

        # Por padrão é obrigatório
        self.assertTrue(field.required)

        # Mas no formulário não é
        self.assertFalse(form.is_required(field))

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Organization
from gatheros_subscription.models import Field


class BaseEventFieldTest(TestCase):
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
    ]

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')

        # Organização que possui mais campos.
        self.organization = Organization.objects.get(slug='diego-tolentino')

    def _login(self):
        self.client.force_login(self.user)


class FormFieldsViewTest(BaseEventFieldTest):
    def _get_url(self, organization=None):
        if not organization:
            organization = self.organization

        return reverse('subscription:fields', kwargs={
            'organization_pk': organization.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_different_organization(self):
        members = self.user.person.members.all()
        org_pks = [member.organization.pk for member in members]

        # Nenhuma das organizações do usuário
        organization = Organization.objects.exclude(pk__in=org_pks).first()

        url = self._get_url(organization=organization)
        response = self.client.get(url, follow=True)

        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_not_member(self):
        """
        Não permite ação para campo cuja organização o usuário não é membro.
        """
        user = User.objects.get(email='lucianasilva@gmail.com')
        self.client.force_login(user)

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')


class FormFieldAddViewTest(BaseEventFieldTest):
    def _get_url(self, organization=None):
        if not organization:
            organization = self.organization

        return reverse('subscription:field-add', kwargs={
            'organization_pk': organization.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_not_member(self):
        """
        Não permite ação para campo cuja organização o usuário não é membro.
        """
        user = User.objects.get(email='lucianasilva@gmail.com')
        self.client.force_login(user)

        response = self.client.get(self._get_url(), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_add(self):
        """ Testa adição pela view. """
        self._login()

        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'name': 'Um evento de teste 111',
            'label': 'Um evento de teste 111',
            'active': False,
        }

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Campo criado com sucesso')


class FormFieldEditViewTest(BaseEventFieldTest):
    # noinspection PyMethodMayBeStatic
    def _get_url(self, field):
        return reverse('subscription:field-edit', kwargs={'pk': field.pk})

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        field = self.organization.fields.filter(
            form_default_field=False
        ).first()
        response = self.client.get(self._get_url(field), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        field = self.organization.fields.filter(
            form_default_field=False
        ).first()
        response = self.client.get(self._get_url(field))
        self.assertEqual(response.status_code, 200)

    def test_not_member(self):
        """
        Não permite ação para campo cuja organização o usuário não é membro.
        """
        user = User.objects.get(email='lucianasilva@gmail.com')
        self.client.force_login(user)

        field = self.organization.fields.filter(
            form_default_field=False
        ).first()
        response = self.client.get(self._get_url(field), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_edit_default_field(self):
        """ Testa edição de campo fixo pela view. """
        self._login()

        field = self.organization.fields.filter(
            form_default_field=True
        ).first()

        data = {'field_type': Field.FIELD_INPUT_TEXT}

        response = self.client.post(
            self._get_url(field=field),
            data=data,
            follow=True
        )
        self.assertContains(response, 'Este campo não pode ser editado')

    def test_edit(self):
        """ Testa edição pela view. """
        self._login()

        field = self.organization.fields.filter(
            form_default_field=False
        ).first()

        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': field.name + ' edited',
        }

        response = self.client.post(
            self._get_url(field=field),
            data=data,
            follow=True
        )
        self.assertContains(response, 'Campo alterado com sucesso')

        field = Field.objects.get(pk=field.pk)
        self.assertEqual(field.field_type, data['field_type'])
        self.assertEqual(field.label, data['label'])


class FormFieldDeleteViewTest(BaseEventFieldTest):
    # noinspection PyMethodMayBeStatic
    def _get_url(self, field):
        return reverse('subscription:field-delete', kwargs={
            'pk': field.pk
        })

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        field = self.organization.fields.filter(
            form_default_field=False
        ).first()
        response = self.client.get(self._get_url(field), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        field = self.organization.fields.filter(
            form_default_field=False
        ).first()
        response = self.client.get(self._get_url(field))
        self.assertEqual(response.status_code, 200)

    def test_not_member(self):
        """
        Não permite ação para campo cuja organização o usuário não é membro.
        """
        user = User.objects.get(email='lucianasilva@gmail.com')
        self.client.force_login(user)

        field = self.organization.fields.filter(
            form_default_field=False
        ).first()

        response = self.client.get(self._get_url(field), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_delete_not_allowed(self):
        """ Testa exclusão de campo fixo pela view. """
        self._login()

        field = self.organization.fields.filter(
            form_default_field=True
        ).first()

        response = self.client.post(self._get_url(field), follow=True)
        self.assertContains(response, 'Você não pode excluir este registro')

    def test_delete(self):
        """ Testa exclusão de campo pela view. """
        self._login()
        field = self.organization.fields.filter(
            form_default_field=False
        ).first()
        response = self.client.post(self._get_url(field), follow=True)
        self.assertContains(response, 'Campo excluído com sucesso')

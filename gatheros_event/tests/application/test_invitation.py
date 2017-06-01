# test_resend_invitation_differente_type(self):
# test_expiration_days_as_configured(self):
from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.test import TestCase

from gatheros_event.forms import InvitationCreateForm
from gatheros_event.models import Invitation, Member, Organization, Person


class InvitationCreateFormTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_form(self, username="lucianasilva@gmail.com", data=None):
        user = User.objects.get(username=username)
        return InvitationCreateForm(user, data)

    def test_init_without_user(self):
        """
        Form sem usuário deve emitir um exception
        """
        with self.assertRaises(TypeError):
            InvitationCreateForm()

    def test_init_with_user_without_data(self):
        """
        Form sem dados deve mostrar erros de validação
        """
        form = self._get_form(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('organization', form.errors)
        self.assertIn('to', form.errors)

    def test_render_form(self):
        """
        Se na apresentação do formulário aparece as organizações que é
        permitido convidar, e não aparece as que não é
        """
        form = self._get_form()
        rendered = form.as_ul()
        self.assertIn("In2 Web Soluções e Serviços", rendered)
        self.assertNotIn("/MNT", rendered)
        self.assertNotIn("Luciana Silva", rendered)

    def test_send_invite(self):
        """
        Se o convite foi enviado por email
        """
        form = self._get_form(data={
            'organization': 5,
            'group': Member.HELPER,
            'to': 'joao@teste.com,'
                  'diegotolentino@gmail.com'
        })
        form.is_valid()
        form.send_invite()
        self.assertEqual(len(mail.outbox), 2)


class InvitationCreateViewTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.force_login(self.user)
        self.url = reverse('gatheros_event:invitation')
        self.url_success = reverse('gatheros_event:invitation-success')
        organization = Organization.objects \
            .get(slug="in2-web-solucoes-e-servicos")
        self.data = {
            'organization': organization.pk,
            'group': Member.HELPER,
            'to': 'joao@teste.com,'
                  'diegotolentino@gmail.com'
        }

    def test_get_ok(self):
        """
        Retornar a página com o formulário deve ser ok
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_emails_post(self):
        """
        Email inválido
        """
        self.data.update({'to': '123'})
        response = self.client.post(self.url, self.data)
        self.assertNotContains(response, "Este campo é obrigatório")
        self.assertContains(response, "não é um email válido.")

    def test_invalid_organization_post(self):
        """
        Sem organização
        """
        self.data.pop('organization')
        response = self.client.post(self.url, self.data)
        self.assertContains(response, "Este campo é obrigatório")
        self.assertNotContains(response, "não é um email válido")

    def test_invite_to_foreign_organization(self):
        """
        Organização que o usuário não é membro
        """
        self.data.update({'organization': 7})
        response = self.client.post(self.url, self.data)
        self.assertContains(response, "Sua escolha não é uma das disponíveis.")

    def test_not_allowed_to_invite_organization(self):
        """
        Organização que o usuário é membro mas não é admin
        """
        self.data.update({'organization': 2})
        response = self.client.post(self.url, self.data)
        self.assertContains(response, "Sua escolha não é uma das disponíveis.")

    def test_invite_already_organization_member(self):
        """
        Convidar um email de uma pessoa que já está na organização
        """
        self.data.update(
            {
                'to': 'flavia@in2web.com.br'
            }
        )
        response = self.client.post(self.url, self.data)
        self.assertRegex(
            response.content.decode("utf-8"),
            r'Um membro com o email .* já existe na organização .*.'
        )

    def test_invite_sent_success_redirect(self):
        """
        Ao enviar um convite com sucesso, redireciona o usuário paga
        pagina de sucesso
        """
        self.assertEqual(Invitation.objects.count(), 0)
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, self.url_success)
        response = self.client.get(self.url_success)
        self.assertContains(response, "Convite(s) enviado(s) com sucesso.")

    def test_invite_sent_success_has_outbox_email(self):
        """
        Ao enviar um convite com sucesso, tem email na caixa de saída
        """
        self.client.post(self.url, self.data)
        self.assertEqual(len(mail.outbox), 2)


class InvitationDecisionViewWithProfile(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '012_invitation',
    ]

    def setUp(self):
        self.to = User.objects.get(email="lucianasilva@gmail.com")
        self.wrong_to = User.objects.get(email="flavia@in2web.com.br")
        self.invite_pk = Invitation.objects.get(
            author__person__email="flavia@in2web.com.br",
            author__organization__slug="paroquias-unidas",
            to=self.to
        ).pk

        self.url = reverse(
            'gatheros_event:invitation-decision',
            kwargs={
                'pk': self.invite_pk
            }
        )
        self.url_redirect = reverse('gatheros_front:login')

    def test_get_without_login(self):
        """
        Retornar a página com o formulário deve ser ok
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, self.url_redirect)

    def test_get_with_login(self):
        """
        Retornar a página com o formulário deve ser ok
        """
        self.client.force_login(user=self.to)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_with_wrong_login(self):
        """
        O usuário logado não é o mesmo do convite
        """
        self.client.force_login(user=self.wrong_to)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'Usuário do convite é diferente do logado'
        )

    def test_post_errado(self):
        """
        Post sem informação de aceite ou recusado
        """
        with self.assertRaises(ValidationError):
            self.client.post(self.url, {})

    def test_post_decline(self):
        """
        Post ignorando o convite
        """
        response = self.client.post(
            self.url,
            {
                'invitation_decline': 'invitation_decline'
            }
        )
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(Invitation.DoesNotExist):
            Invitation.objects.get(pk=self.invite_pk)

    def test_post_accept(self):
        """
        Post aceitando o convite deve direcionar para o inicio
        """
        self.client.force_login(user=self.to)
        response = self.client.post(
            self.url,
            {
                'invitation_accept': 'invitation_accept'
            }
        )
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Invitation.DoesNotExist):
            Invitation.objects.get(pk=self.invite_pk)


class InvitationDecisionViewWithoutProfileTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '012_invitation',
    ]

    def setUp(self):
        self.to = User.objects.get(email="joao-das-couves@gmail.com")
        self.wrong_to = User.objects.get(email="flavia@in2web.com.br")
        self.invite_pk = Invitation.objects.get(
            author__person__email="flavia@in2web.com.br",
            author__organization__slug="paroquias-unidas",
            to=self.to
        ).pk

        self.url = reverse(
            'gatheros_event:invitation-decision',
            kwargs={
                'pk': self.invite_pk
            }
        )
        self.url_login = reverse(
            'gatheros_front:login'
        )
        self.url_profile = reverse(
            'gatheros_event:invitation-profile',
            kwargs={
                'pk': self.invite_pk
            }
        )

    def test_get(self):
        """
        Retornar a página com o formulário deve ser 200 - ok por que o usuário
        está inativo pois não possui perfil
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_decline(self):
        """
        Post ignorando o convite
        """
        response = self.client.post(
            self.url,
            {
                'invitation_decline': 'invitation_decline'
            }
        )
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(Invitation.DoesNotExist):
            Invitation.objects.get(pk=self.invite_pk)

    def test_post_accept_user_without_profile(self):
        """
        Post aceitando o convite e mostra o form para criando um perfil
        """
        response = self.client.post(
            self.url,
            {
                'invitation_accept': 'invitation_accept'
            }
        )

        self.assertRedirects(response, self.url_profile)
        self.assertEqual(
            Invitation.objects.get(pk=self.invite_pk).pk,
            self.invite_pk
        )


class InvitationProfileViewTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '012_invitation',
    ]

    def setUp(self):
        self.to = User.objects.get(email="joao-das-couves@gmail.com")
        self.wrong_to = User.objects.get(email="flavia@in2web.com.br")
        invite = Invitation.objects.get(
            author__person__email="flavia@in2web.com.br",
            author__organization__slug="paroquias-unidas",
            to=self.to
        )

        self.invite_pk = invite.pk
        self.organization = invite.author.organization
        self.url = reverse(
            'gatheros_event:invitation-profile',
            kwargs={
                'pk': self.invite_pk
            }
        )

        self.url_success = reverse(
            'gatheros_event:organization-panel'
        )

        self.data = {
            # Informações do perfil
            "name": "João das Couves",
            "gender": "M",
            "email": "joao-das-couves@gmail.com",
            "city": 5413,

            # Senha do novo usuário
            'new_password1': '123',
            'new_password2': '123',
        }

    def test_get(self):
        """
        Retorna página com form para criação do perfil e senha
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_profile_created(self):
        """
        Post cria um perfil
        """
        response = self.client.post(
            self.url,
            self.data
        )

        self.assertEqual(response.status_code, 302)

        self.assertNotIsInstance(
            self.to,
            Person,
            'Perfil de usuário não foi criado'
        )

    def test_post_member_created(self):
        """
        Post cria um membro na organização
        """
        self.client.post(
            self.url,
            self.data
        )

        try:
            Member.objects.get(
                organization=self.organization,
                person=self.to.person
            )
        except Member.DoesNotExist:
            self.fail('Membro não foi criado')

    def test_post_invitation_removed(self):
        """
        Post remove o convite
        """
        self.client.post(
            self.url,
            self.data
        )

        with self.assertRaises(Invitation.DoesNotExist):
            Invitation.objects.get(pk=self.invite_pk)

""" Testes de aplicação com `Invitation`. """

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.test import TestCase

from gatheros_event import settings
from gatheros_event.forms import InvitationCreateForm
from gatheros_event.models import Invitation, Member, Organization, Person


class InvitationCreateFormTest(TestCase):
    """ Testes de criação de `Invitation` """
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_form(
            self,
            initial=None,
            username="lucianasilva@gmail.com",
            data=None
    ):
        user = User.objects.get(username=username)
        return InvitationCreateForm(user=user, initial=initial, data=data)

    # noinspection PyMethodMayBeStatic
    def _get_organization(self):
        return Organization.objects.get(slug='in2-web-solucoes-e-servicos')

    def test_init_without_user(self):
        """
        Form sem usuário deve emitir um exception
        """
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            InvitationCreateForm()

    def test_init_with_user_without_data(self):
        """
        Form sem dados deve mostrar erros de validação
        """
        form = self._get_form(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('to', form.errors)

    def test_send_invite(self):
        """
        Se o convite foi enviado por email
        """
        form = self._get_form(
            initial={'organization': self._get_organization()},
            data={'to': 'joao@teste.com, diegotolentino@gmail.com'}
        )
        self.assertTrue(form.is_valid())
        if form.errors:
            print(form.errors)

        form.send_invite()
        self.assertEqual(len(mail.outbox), 2)


class InvitationCreateViewTest(TestCase):
    """ Testes de criação de `Invitation` pela view """
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
        self.organization = Organization.objects.get(
            slug="in2-web-solucoes-e-servicos"
        )
        self.url = reverse('event:invitation-add', kwargs={
            'organization_pk': self.organization.pk
        })
        self.data = {'to': 'joao@teste.com, diegotolentino@gmail.com'}

    def test_get_ok(self):
        """
        Retornar a página com o formulário deve ser ok
        """
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_invalid_emails_post(self):
        """
        Email inválido
        """
        self.data.update({'to': '123'})
        response = self.client.post(self.url, self.data, follow=True)
        self.assertNotContains(response, "Este campo é obrigatório")
        self.assertContains(response, "não é um email válido.")

    def test_not_allowed_to_invite_organization(self):
        """
        Organização que o usuário é membro mas não é admin
        """
        url = reverse('event:invitation-add', kwargs={
            'organization_pk': 6
        })
        response = self.client.post(url, self.data, follow=True)
        self.assertContains(response, "Você não pode realizar esta ação.")

    def test_invite_already_organization_member(self):
        """
        Convidar um email de uma pessoa que já está na organização
        """
        self.data.update(
            {
                'to': 'flavia@in2web.com.br'
            }
        )
        response = self.client.post(self.url, self.data, follow=True)
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
        response = self.client.post(self.url, self.data, follow=True)
        self.assertContains(response, "Convite(s) enviado(s) com sucesso.")

    def test_invite_sent_success_has_outbox_email(self):
        """
        Ao enviar um convite com sucesso, tem email na caixa de saída
        """
        self.client.post(self.url, self.data)
        self.assertEqual(len(mail.outbox), 2)


class InvitationDecisionViewWithProfile(TestCase):
    """ Testes de decisão de aceite/recusa de `Invitation` pela view. """
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

        self.url = reverse('public:invitation-decision', kwargs={
            'pk': self.invite_pk
        })
        self.url_redirect = reverse('front:login')

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
    """
    Testes de decisão de aceite/recusa de `Invitation` pela view de usuário sem
    vínculo com `Person`.
    """
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

        self.url = reverse('public:invitation-decision', kwargs={
            'pk': self.invite_pk
        })
        self.url_login = reverse(
            'front:login'
        )
        self.url_profile = reverse(
            'public:invitation-profile',
            kwargs={'pk': self.invite_pk}
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
    """ Testes criação de perfil pela view. """
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
            'public:invitation-profile',
            kwargs={'pk': self.invite_pk}
        )

        self.url_success = reverse(
            'event:invitation-list',
            kwargs={
                'organization_pk': self.organization.pk
            }
        )

        self.data = {
            # Informações do perfil
            "name": "João das Couves",
            "gender": "M",
            "email": "joao-das-couves@gmail.com",
            "city": 5413,

            # Senha do novo usuário
            'new_password1': '3510',
            'new_password2': '3510',
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
        response = self.client.post(self.url, self.data)

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

        self.assertIsInstance(
            Member.objects.get(
                organization=self.organization,
                person=self.to.person
            ),
            Member
        )

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

    def test_post_user_can_login(self):
        """
        Apos aceitar o convite e criar o perfil o usuário deve ser capaz
        de acessar o sistema com a senha informada
        """
        self.client.post(
            self.url,
            self.data
        )

        self.assertTrue(
            self.client.login(
                username=self.data["email"],
                password=self.data['new_password1'],
            )
        )


class InvitationDeleteViewTest(TestCase):
    """ Testes de exclusão de `Invitation` pela view. """
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
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.force_login(self.user)

    def test_delete(self):
        """ Testa exclusão de convite. """
        member = self.user.person.members.first()
        invitation = Invitation.objects.filter(author=member).first()

        url = reverse('event:invitation-delete', kwargs={
            'organization_pk': invitation.author.organization.pk,
            'pk': invitation.pk
        })
        response = self.client.post(url, {'pk': invitation.pk}, follow=True)
        self.assertContains(response, 'Convite excluído com sucesso.')


class InvitationRenewViewTest(TestCase):
    """ Testes de renovação de `Invitation` pela view"""
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
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.force_login(self.user)

    def test_renew(self):
        """ Testa renovação de convite. """
        now = datetime.now()
        created_date = now - timedelta(days=30)

        days = settings.INVITATION_ACCEPT_DAYS
        expire_date = created_date + timedelta(days=days)

        # Altera convite como antigo
        member = self.user.person.members.first()
        invitation = Invitation.objects.filter(author=member).first()
        invitation.created = created_date
        invitation.expired = expire_date
        invitation.save()

        self.assertTrue(invitation.is_expired)

        url = reverse('event:invitation-resend', kwargs={
            'organization_pk': invitation.author.organization.pk,
            'pk': invitation.pk
        })
        response = self.client.post(url, {'pk': invitation.pk}, follow=True)
        self.assertContains(response, 'Convite renovado com sucesso.')

        invitation = Invitation.objects.get(pk=invitation.pk)
        self.assertFalse(invitation.is_expired)

    def test_renew_not_expired(self):
        """ Testa renovação de convites que ainda não expiraram. """
        created_date = datetime.now()

        days = settings.INVITATION_ACCEPT_DAYS
        expire_date = created_date + timedelta(days=days)

        # Altera convite como antigo
        member = self.user.person.members.first()
        invitation = Invitation.objects.filter(author=member).first()

        invitation.created = created_date
        invitation.expired = expire_date
        invitation.save()

        self.assertFalse(invitation.is_expired)

        url = reverse('event:invitation-resend', kwargs={
            'organization_pk': invitation.author.organization.pk,
            'pk': invitation.pk
        })
        response = self.client.post(url, {'pk': invitation.pk}, follow=True)
        self.assertContains(
            response,
            'O convite não está expirado e não precisa ser renovado.'
        )

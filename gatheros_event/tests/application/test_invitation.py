# test_resend_invitation_differente_type(self):
# test_expiration_days_as_configured(self):
from django.contrib.auth.models import User
from django.core import mail
from django.shortcuts import reverse
from django.test import TestCase

from gatheros_event.forms import InvitationForm
from gatheros_event.models import Invitation


class InvitationFormTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def _get_form(self, username="lucianasilva@gmail.com", data=None):
        user = User.objects.get(username=username)
        return InvitationForm(user, data)

    def test_init_without_user(self):
        """
        Form sem usuário deve emitir um exception
        """
        with self.assertRaises(TypeError):
            InvitationForm()

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
            'to': 'joao@teste.com,'
                  'diegotolentino@gmail.com'
        })
        form.is_valid()
        form.send_invite()
        self.assertEqual(len(mail.outbox), 2)


class InviteViewTest(TestCase):
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
        self.url = reverse('gatheros_event:organization-invite')
        self.url_success = reverse(
            'gatheros_event:organization-invite-success')
        self.data = {
            'organization': 5,
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

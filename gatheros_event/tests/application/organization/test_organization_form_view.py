""" Testes de aplicação com `Organization` - Formulários pela view. """
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from gatheros_event.models import Organization


class OrganizationFormViewTest(TestCase):
    """ Testes de formulário de organização pela view. """
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    # noinspection PyMethodMayBeStatic
    def _get_url(self):
        """ Resgata URL. """
        return reverse_lazy('event:organization-add')

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_add(self):
        """ Testa criação de organização pela view. """
        self._login()
        data = {
            'name': 'Added organization',
            'description_html': '<p style="color:red>Some text</p>',
        }

        response = self.client.post(
            path=reverse_lazy('event:organization-add'),
            data=data,
            follow=True
        )
        self.assertContains(
            response,
            "Organização criada com sucesso."
        )

    def test_add_internal(self):
        """ Testa criação de organização interna pela view. """

        # Usuário que não possui organização interna
        user = User.objects.get(username="hugoseabra19@gmail.com")
        self.client.force_login(user)

        response = self.client.post(
            path=reverse_lazy('event:organization-add-internal'),
            follow=True
        )
        self.assertContains(
            response,
            "Organização criada com sucesso"
        )

    def test_edit(self):
        """ Testa edição de organização pela view. """
        self._login()
        org = Organization.objects.get(slug='in2-web-solucoes-e-servicos')
        data = {
            'name': org.name + ' edited',
            'description_html': '<p style="color:red>Some text</p>',
        }

        response = self.client.post(
            path=reverse('event:organization-edit', kwargs={
                'pk': org.pk
            }),
            data=data,
            follow=True
        )
        self.assertContains(
            response,
            "Organização alterada com sucesso."
        )

        org = Organization.objects.get(pk=org.pk)
        self.assertEqual(org.name, data['name'])
        self.assertEqual(org.description_html, data['description_html'])

    def test_delete(self):
        """ Testa exclusão de organização pela view. """
        self._login()
        org = Organization.objects.get(slug='in2-web-solucoes-e-servicos')

        response = self.client.post(
            follow=True,
            path=reverse('event:organization-delete', kwargs={
                'pk': org.pk
            })
        )
        self.assertContains(
            response,
            "Organização excluída com sucesso."
        )

        with self.assertRaises(Organization.DoesNotExist):
            Organization.objects.get(pk=org.pk)

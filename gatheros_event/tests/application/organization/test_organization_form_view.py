from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from gatheros_event.models import Organization


# @TODO Testar upload de avatar

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


class OrganizationFormAddTest(TestCase):
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.force_login(self.user)

    def test_add(self):
        """ Testa criação de organização pela view. """
        data = {
            'name': 'Added organization',
            'description_html': '<p style="color:red>Some text</p>',
        }

        response = self.client.post(
            path=reverse_lazy('gatheros_event:organization-add'),
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
            path=reverse_lazy('gatheros_event:organization-add-internal'),
            follow=True
        )
        self.assertContains(
            response,
            "Organização criada com sucesso"
        )

    def test_edit(self):
        """ Testa edição de organização pela view. """

        org = Organization.objects.get(slug='in2-web-solucoes-e-servicos')
        data = {
            'name': org.name + ' edited',
            'description_html': '<p style="color:red>Some text</p>',
        }

        response = self.client.post(
            path=reverse('gatheros_event:organization-edit', kwargs={
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

        org = Organization.objects.get(slug='in2-web-solucoes-e-servicos')

        response = self.client.post(
            follow=True,
            path=reverse('gatheros_event:organization-delete', kwargs={
                'pk': org.pk
            })
        )
        self.assertContains(
            response,
            "Organização excluída com sucesso."
        )

        with self.assertRaises(Organization.DoesNotExist):
            Organization.objects.get(pk=org.pk)

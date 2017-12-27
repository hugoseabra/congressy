""" Testes de aplicação com `Place` - Formulários pela view. """
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Member, Place


class PlaceFormViewTest(TestCase):
    """ Testes de formulário de local de evento pela view. """
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
        self.organization = self._get_organization()

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_organization(self):
        """ Resgata instância de Organization. """
        member = self.user.person.members.filter(group=Member.ADMIN).first()
        assert member is not None
        return member.organization

    def test_add_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        url = reverse('event:place-add', kwargs={
            'organization_pk': self.organization.pk
        })
        response = self.client.get(url, follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=' + url
        self.assertRedirects(response, redirect_url)

    def test_edit_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        place = Place.objects.filter(organization=self.organization).first()
        url = reverse('event:place-edit', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })
        response = self.client.get(url, follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=' + url
        self.assertRedirects(response, redirect_url)

    def test_delete_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        place = Place.objects.filter(organization=self.organization).first()
        url = reverse('event:place-delete', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })
        response = self.client.get(url, follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=' + url
        self.assertRedirects(response, redirect_url)

    def test_add_status_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        url = reverse('event:place-add', kwargs={
            'organization_pk': self.organization.pk
        })
        result = self.client.get(url)
        self.assertEqual(result.status_code, 200)

    def test_edit_status_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        place = Place.objects.filter(organization=self.organization).first()
        url = reverse('event:place-edit', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })
        result = self.client.get(url)
        self.assertEqual(result.status_code, 200)

    def test_delete_status_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        place = Place.objects.filter(organization=self.organization).first()

        # Remove relação para permitir exclusão.
        for event in place.events.all():
            event.place = None
            event.save()

        url = reverse('event:place-delete', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })
        result = self.client.get(url)
        self.assertEqual(result.status_code, 200)

    def test_add(self):
        """ Testa adição de local de evento. """
        self._login()
        name = 'New Place'
        city = 5337

        url = reverse('event:place-add', kwargs={
            'organization_pk': self.organization.pk
        })

        response = self.client.post(url, follow=True, data={
            'name': name,
            'city': city,
            'organization': self.organization.pk
        })
        self.assertContains(response, 'Local criado com sucesso.')

    def test_edit(self):
        """ Testa edição de local. """
        self._login()
        place = Place.objects.filter(organization=self.organization).first()

        name = place.name + ' edited'
        city = 5337

        url = reverse('event:place-edit', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })

        response = self.client.post(url, follow=True, data={
            'name': name,
            'city': city,
            'organization': self.organization.pk
        })
        self.assertContains(response, 'Local alterado com sucesso.')

    def test_delete_not_allowed(self):
        """ Testa restrição ao excluir local. """
        self._login()
        place = Place.objects.filter(organization=self.organization).first()

        url = reverse('event:place-delete', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })
        response = self.client.post(url, follow=True)
        self.assertContains(
            response,
            'Você não pode excluir este registro'
        )

    def test_delete(self):
        """ Testa exclusão de local. """
        self._login()
        place = Place.objects.filter(
            organization=self.organization
        ).exclude(events__isnull=True).first()

        # Remove local dos eventos
        for event in place.events.all():
            event.place = None
            event.save()

        url = reverse('event:place-delete', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })

        response = self.client.post(url, follow=True)
        self.assertContains(response, 'Local excluído com sucesso.')

        with self.assertRaises(Place.DoesNotExist):
            Place.objects.get(pk=place.pk)

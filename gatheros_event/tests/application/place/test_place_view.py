from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Member, Place, Event


class PlaceFormViewTest(TestCase):
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
        self.client.force_login(self.user)

    def _get_organization(self):
        member = self.user.person.members.filter(group=Member.ADMIN).first()
        assert member is not None
        return member.organization

    def test_add(self):
        name = 'New Place'
        city = 5337

        url = reverse('gatheros_event:place-add', kwargs={
            'organization_pk': self.organization.pk
        })

        response = self.client.post(url, follow=True, data={
            'name': name,
            'city': city,
            'organization': self.organization.pk
        })
        self.assertContains(response, 'Local criado com sucesso.')

    def test_edit(self):
        place = Place.objects.filter(organization=self.organization).first()

        name = place.name + ' edited'
        city = 5337

        url = reverse('gatheros_event:place-edit', kwargs={
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
        event = Event.objects.filter(
            organization=self.organization
        ).exclude(place__isnull=True).first()
        place = event.place

        url = reverse('gatheros_event:place-delete', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })

        response = self.client.post(url, follow=True)
        self.assertContains(
            response,
            'Você não pode excluir este registro.'
        )

    def test_delete(self):
        place = Place.objects.filter(
            organization=self.organization
        ).exclude(events__isnull=True).first()

        # Remove local dos eventos
        for event in place.events.all():
            event.place = None
            event.save()

        url = reverse('gatheros_event:place-delete', kwargs={
            'organization_pk': self.organization.pk,
            'pk': place.pk
        })

        response = self.client.post(url, follow=True)
        self.assertContains(response, 'Local excluído com sucesso.')

        with self.assertRaises(Place.DoesNotExist):
            Place.objects.get(pk=place.pk)

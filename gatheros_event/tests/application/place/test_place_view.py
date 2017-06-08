from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy

from gatheros_event.models import Member


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
        self.url = reverse_lazy('gatheros_event:organization-add-place')

    def _get_organization(self):
        member = self.user.person.members.filter(group=Member.ADMIN).first()
        assert member is not None
        return member.organization

    def test_add_place(self):
        name = 'New Place'
        city = 5337

        response = self.client.post(self.url, follow=True, data={
            'name': name,
            'city': city,
            'organization': self.organization.pk
        })
        self.assertContains(response, 'Local adicionado com sucesso.')

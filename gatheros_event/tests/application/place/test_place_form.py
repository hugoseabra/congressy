from django.test import TestCase

from gatheros_event.forms import PlaceForm
from gatheros_event.models import Organization, Place


class PlaceFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_organization(self):
        return Organization.objects.get(slug='mnt')

    def test_add_local(self):
        organization = self._get_organization()
        num_places = organization.places.count()
        assert num_places > 0

        name = 'New Place'
        city = 5337

        form = PlaceForm(data={
            'name': name,
            'city': city,
            'organization': organization.pk
        })
        self.assertTrue(form.is_valid())
        form.save()

        organization = self._get_organization()
        self.assertEqual(organization.places.count(), num_places + 1)

        place = Place.objects.get(name=name, city=city)
        self.assertIsInstance(place, Place)

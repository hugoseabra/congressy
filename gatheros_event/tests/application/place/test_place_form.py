""" Testes de aplicação com `Place` - Formulários. """
import tempfile

from django.test import TestCase
from django.test.utils import override_settings

from gatheros_event.forms import PlaceForm
from gatheros_event.models import Organization, Place


class PlaceFormTest(TestCase):
    """ Testes de formulário de local de evento. """
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_organization(self):
        return Organization.objects.get(slug='mnt')

    def test_add(self):
        """ Testa adição de local. """
        organization = self._get_organization()
        num_places = organization.places.count()
        self.assertGreater(num_places, 0)

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

    def test_edit(self):
        """ Testa edição de local. """
        organization = self._get_organization()
        place = Place.objects.filter(organization=organization).first()
        num_places = organization.places.count()
        assert num_places > 0

        name = place.name + ' edited'
        city = 5319

        form = PlaceForm(instance=place, data={
            'name': name,
            'city': city,
            'organization': organization.pk
        })
        if not form.is_valid():
            print(form.errors)

        self.assertTrue(form.is_valid())
        form.save()

        place = Place.objects.get(pk=place.pk)
        self.assertEqual(place.name, name)
        self.assertEqual(place.city.pk, city)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_add_streetview_link(self):
        """ Testa adição de local com link do streetview. """
        organization = self._get_organization()
        num_places = organization.places.count()
        self.assertGreater(num_places, 0)

        form = PlaceForm(data={
            'name': 'Modul Espaço Coworking',
            'city': 5337,
            'organization': organization.pk,
            'google_streetview_link':
                'https://www.google.com.br/maps/'
                '@-16.6876661,-49.2621363,3a,75y,312.66h,93.91t/'
                'data=!3m6!1e1!3m4!1swYXmnl0vlXvZmkXXqRlNog!2e0!7i13312!8i6656'
        })

        # Formulário deve estar válido
        self.assertTrue(form.is_valid())
        instance = form.save()

        # Deve ter um local a mais
        self.assertEqual(organization.places.count(), num_places + 1)

        # Deve ter preenchido a url do maps
        self.assertIsNotNone(
            instance.google_maps_link,
            'Link Google Maps não preenchido'
        )
        self.assertGreater(len(instance.google_maps_link), 0)

        # Campo ImageFile deve estar preenchido
        for field_name in ['google_maps_img', 'google_streetview_img']:
            self.assertTrue(
                bool(getattr(instance, field_name)),
                'Campo "%s" não está preenchido' % field_name
            )

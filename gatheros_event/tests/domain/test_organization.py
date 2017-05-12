from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from gatheros_event.models import Organization


class OrganizationModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '004_category',
        '007_organization',
        '009_place',
        '010_event',
    ]

    def test_nao_exclui_se_possui_eventos(self):
        organization = Organization.objects.annotate(
            num_events=Count('events')
        ).filter(num_events__gt=0).first()

        with self.assertRaises(ProtectedError):
            organization.delete()

        for event in organization.events.all():
            event.delete()

        # Agora funciona
        organization.delete()

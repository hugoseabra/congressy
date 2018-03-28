""" Testes de managers do módulo de Afiliados. """

from test_plus.test import TestCase
from datetime import datetime, timedelta
from affiliate import managers
from gatheros_event.models import Event, Organization, Category


class AffiliationManagerTest(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            organization=Organization.objects.create(name='some org'),
            category=Category.objects.create(name='some cat'),
            name='Evento teste',
            subscription_type=Event.SUBSCRIPTION_BY_LOTS,
            date_start=datetime.now(),
            date_end=datetime.now() + timedelta(hours=8)
        )

    def test_cannot_edit_links(self):
        # manager = managers.AffiliationManager(data={
        #     'event':
        # })
        pass

    def test_error_when_max_percent_exceeded(self):
        pass

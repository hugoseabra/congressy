""" Testes de managers do módulo de Afiliados. """

from affiliate import services, constants
from base.tests.test_suites import ApplicationServicePersistenceTestCase
from ..mock_factory import MockFactory


class AffiliateServicePersistenceTest(ApplicationServicePersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.AffiliateService
    required_fieds = ('person',)
    data_edit_to = {
        'recipient_id': 'bbbbbbb',
        'status': constants.SUSPENDED,
    }

    def setUp(self):
        mock_factory = MockFactory()
        person = mock_factory.create_fake_person()

        self.data = {
            'person': person.pk,
            'recipient_id': 'aaaaaaaaaa',
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class AffiliationServicePersistenceTest(ApplicationServicePersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.AffiliationService
    required_fieds = ('event', 'affiliate',)
    data_edit_to = {
        'percent': 11.0,
    }

    def setUp(self):
        mock_factory = MockFactory()
        event = mock_factory.create_fake_event()
        affiliate = mock_factory.create_fake_affiliate()

        self.data = {
            'event': event.pk,
            'affiliate': affiliate.pk,
            'percent': 10.0,
            'link_whatsapp': 'whatsapp.com',
            'link_facebook': 'facebook.com',
            'link_twitter': 'twitter.com',
            'link_direct': 'direct.com',
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()

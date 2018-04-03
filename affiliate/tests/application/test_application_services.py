""" Testes de managers do módulo de Afiliados. """
from django.core.validators import URLValidator
from test_plus.test import TestCase

from affiliate import services, constants
from base.tests.test_suites import ApplicationServicePersistenceTestCase
from ..mock_factory import MockFactory


class AffiliateServicePersistenceTest(ApplicationServicePersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.AffiliateService
    required_fieds = ('person',)
    data_edit_to = {
        'status': constants.SUSPENDED,
    }

    def setUp(self):
        mock_factory = MockFactory()
        person = mock_factory.create_fake_person()

        self.data = {
            'person': person.pk,
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


class AffiliationServiceLinkTest(TestCase):
    """ Testes de links de afiliação. """

    def setUp(self):
        mock_factory = MockFactory()
        affiliate = mock_factory.create_fake_affiliate()

        self.event = mock_factory.create_fake_event()
        self.affiliation = mock_factory.create_fake_affiliation(
            event=self.event,
            affiliate=affiliate,
        )

        self.data = {
            'event': self.event.pk,
            'affiliate': affiliate.pk,
            'percent': 10.0,
        }

        self.service = services.AffiliationService()

    def test_get_event_absolute_link(self):
        validator = URLValidator()
        link = self.service._get_event_absolute_link(event=self.event)

        # Nao levanta um ValidationError
        validator(link)

    def test_create_links(self):
        """ Testa criação de links. """
        data = self.service._create_links(data=self.data)

        for link_field in ('link_direct',
                           'link_whatsapp',
                           'link_facebook',
                           'link_twitter'):
            self.assertIn(link_field, data)

    def test_ignore_external_given_links(self):
        """ Testa se link informado externamente é ignora. """

        # Ignorado e novo gerado
        data = {
            'link_whatsapp': 'whatsapp.com',
            'link_facebook': 'facebook.com',
            'link_twitter': 'twitter.com',
            'link_direct': 'direct.com',
        }

        data.update(self.data)

        data = self.service._create_links(data=data)

        for link_field in ('link_direct',
                           'link_whatsapp',
                           'link_facebook',
                           'link_twitter'):
            # Campos de links permanecem.
            self.assertIn(link_field, data)

            link = data.get(link_field)

            # Links não são iguais os informados externamente.
            self.assertNotEqual(link, data)

        # Ignorando e permanecendo com o mesmo
        data = self.service._create_links(data=data, instance=self.affiliation)

        for link_field in ('link_direct',
                           'link_whatsapp',
                           'link_facebook',
                           'link_twitter'):
            # Campos de links permanecem.
            self.assertIn(link_field, data)

            link = data.get(link_field)

            # Links não são iguais os informados externamente.
            self.assertNotEqual(link, data)

    def test_create_links_when_new(self):
        """ Testa criação de link quando nova afiliação. """
        service = services.AffiliationService(data=self.data)

        self.assertTrue(service.is_valid())

        instance = service.save()

        for link_field in ('link_direct',
                           'link_whatsapp',
                           'link_facebook',
                           'link_twitter'):
            # Campos de links existem, mesmo quando informados
            self.assertTrue(hasattr(instance, link_field))

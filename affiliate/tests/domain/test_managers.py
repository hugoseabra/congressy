""" Testes de managers do módulo de Afiliados. """

from test_plus.test import TestCase

from affiliate import managers, constants
from base.tests.test_suites import ManagerPersistenceTestCase
from ..mock_factory import MockFactory


class AffiliateManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.AffiliateManager
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


class AffiliationManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.AffiliationManager
    required_fieds = (
        'event',
        'affiliate',
        'link_whatsapp',
        'link_facebook',
        'link_twitter',
        'link_direct',
    )
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


class AffiliationManagerTest(TestCase):
    data = None
    event = None
    affiliate = None

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

    def test_cannot_edit_links(self):
        """
        Testa edição de links de um afiliação existete.
        """

        # SUCESSO: nova afialiação criada normalmente
        manager = managers.AffiliationManager(data=self.data)
        valid = manager.is_valid()

        if not valid:
            self.fail(manager.errors)

        affiliation = manager.save()

        data = self.data.copy()
        data.update({
            'link_direct': data['link_direct'] + ' edited',
            'link_whatsapp': data['link_whatsapp'] + ' edited',
            'link_facebook': data['link_facebook'] + ' edited',
            'link_twitter': data['link_twitter'] + ' edited'
        })

        # FALHA: edição de links
        manager = managers.AffiliationManager(
            instance=affiliation,
            data=data
        )
        self.assertFalse(manager.is_valid())

        link_field_names = [
            'link_direct',
            'link_whatsapp',
            'link_facebook',
            'link_twitter'
        ]
        for error in manager.errors:
            self.assertIn(error, link_field_names)

    def test_error_when_max_percent_allowed(self):
        """
        Testa criação de afiliação com percentual permitido.
        """
        managers.AffiliationManager.Meta.model.AFFILIATE_MAX_PERCENTAGE = 30
        manager = managers.AffiliationManager(data=self.data)
        valid = manager.is_valid()

        if not valid:
            self.fail(manager.errors)

        affiliation = manager.save()

        percent = self.data['percent']
        self.assertTrue(affiliation.AFFILIATE_MAX_PERCENTAGE > percent)

    def test_error_when_max_percent_exceeded(self):
        """
        Testa criação de afiliação com percentual maior do que o permitido.
        """
        perc = 5.5
        managers.AffiliationManager.Meta.model.AFFILIATE_MAX_PERCENTAGE = perc
        manager = managers.AffiliationManager(data=self.data)
        self.assertFalse(manager.is_valid())

        for field_name, error in manager.errors.items():
            msg = 'A participação percentual de afiliação não pode' \
                  ' ultrapassar o limite de {0:.2f}%'.format(perc)

            self.assertIn(msg, error)

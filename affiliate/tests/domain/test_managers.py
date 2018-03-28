""" Testes de managers do módulo de Afiliados. """

from test_plus.test import TestCase

from affiliate import managers
from ..mock_factory import MockFactory


class AffiliationManagerTest(TestCase):
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

        # FALHA: edição de links
        manager = managers.AffiliationManager(
            instance=affiliation,
            data=self.data
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

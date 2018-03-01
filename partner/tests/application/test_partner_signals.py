"""
     Partner Signal Tests
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from django.core import mail
from partner.tests.mocks import MockFactory

from partner.models import PartnerContract


class PartnerRegistrationViewTests(TestCase):
    """ Partner signals test implementation """

    def setUp(self):
        self.mock_factory = MockFactory()
        self.person = self.mock_factory._create_fake_person()
        self.organization = self.mock_factory._create_fake_organization()
        self.partner = self.mock_factory._create_fake_partner(self.person)
        self.partner_plan = self.mock_factory._create_fake_partner_plan()
        self.event = self.mock_factory._create_fake_event(self.organization)

    def test_partner_and_event_new_contract_email(self):
        """ Testa se está tudo ok emails após a criação de um novo contrato
        de parceria  """

        contract = PartnerContract(event=self.event, partner=self.partner,
                                   partner_plan=self.partner_plan)

        contract.save()

        # Caixa de mensagens deve possuir um email alertando do vinculo
        self.assertEqual(len(mail.outbox), 1)

    def test_partner_and_event_old_contract_email(self):
        """ Testa se está tudo ok emails após a criação de um novo contrato
        de parceria  """

        contract = PartnerContract(event=self.event, partner=self.partner,
                                   partner_plan=self.partner_plan)

        contract.save()

        # Caixa de mensagens deve possuir um email alertando do vinculo
        self.assertEqual(len(mail.outbox), 1)

        # Empty the test outbox
        mail.outbox = []

        # Caixa de mensagens deve estar vazia
        self.assertEqual(len(mail.outbox), 0)

        new_person = self.mock_factory._create_fake_person()
        contract.person = new_person
        contract.save()

        # Caixa de mensagens não deve possuir um email alertando do vinculo,
        # pois contrato já existia.
        self.assertEqual(len(mail.outbox), 0)



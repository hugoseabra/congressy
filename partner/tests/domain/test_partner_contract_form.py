"""
     Partner Contract Form tests
"""
from django.core import mail
from django.test import TestCase

from partner.forms import PartnerContractForm
from partner.tests.mocks import MockFactory


class PartnerContractFormTest(TestCase):
    """
        Partner Contract Form test implementation
        Business rule #1:  The sum of all partners of the event must not exceed
                            the Congressy defined percentage  of the amount of
                            the total amount
    """

    def setUp(self):
        self.mock_factory = MockFactory()
        self.person = self.mock_factory._create_fake_person()
        self.organization = self.mock_factory._create_fake_organization()
        self.partner = self.mock_factory._create_fake_partner(self.person)
        self.partner_plan = self.mock_factory._create_fake_partner_plan()
        self.event = self.mock_factory._create_fake_event(self.organization)

    def test_regular_form_validation(self):
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })
        self.assertTrue(form.is_valid())

    def test_percent_plan_exceeds_defined_max_percentage(self):
        bad_plan = self.mock_factory._create_fake_partner_plan(percentage=30.5)
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': bad_plan.pk,
            'event': self.event.pk,
        })
        form.full_clean()
        self.assertFalse(form.is_valid())

    def test_partners_exceed_defined_max_percentage(self):
        staging_plan = self.mock_factory._create_fake_partner_plan(
            percentage=15)
        bad_plan = self.mock_factory._create_fake_partner_plan(percentage=5.1)
        good_plan = self.mock_factory._create_fake_partner_plan(percentage=5)

        # Staging plan
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': staging_plan.pk,
            'event': self.event.pk,
        })

        self.assertTrue(form.is_valid())
        form.save()

        # Bad Plan
        bad_person = self.mock_factory._create_fake_person()
        bad_partner = self.mock_factory._create_fake_partner(bad_person)
        form = PartnerContractForm(data={
            'partner': bad_partner.pk,
            'partner_plan': bad_plan.pk,
            'event': self.event.pk,
        })
        self.assertFalse(form.is_valid())

        # Good Plan
        good_person = self.mock_factory._create_fake_person()
        good_partner = self.mock_factory._create_fake_partner(good_person)

        form = PartnerContractForm(data={
            'partner': good_partner.pk,
            'partner_plan': good_plan.pk,
            'event': self.event.pk,
        })
        self.assertTrue(form.is_valid())
        form.save()

    def test_same_event_same_partner_add(self):

        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })
        self.assertTrue(form.is_valid())
        form.save()

        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })

        self.assertFalse(form.is_valid())

    def test_same_event_same_partner_edit(self):

        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })
        self.assertTrue(form.is_valid())
        form.save()

        form = PartnerContractForm(
            instance=form.instance,
            data={
                'partner': self.partner.pk,
                'partner_plan': self.partner_plan.pk,
                'event': self.event.pk,
            }
        )

        self.assertTrue(form.is_valid())

    def test_same_event_different_partner(self):
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })
        self.assertTrue(form.is_valid())

        different_person = self.mock_factory._create_fake_person()
        different_partner = self.mock_factory._create_fake_partner(
            person=different_person)

        form = PartnerContractForm(data={
            'partner': different_partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })
        self.assertTrue(form.is_valid())

    def test_partner_and_event_new_contract_email(self):
        """ Testa se está tudo ok emails após a criação de um novo contrato
        de parceria  """

        contract = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })

        contract.save()

        # Caixa de mensagens deve possuir um email alertando do vinculo
        self.assertEqual(len(mail.outbox), 1)

    def test_partner_and_event_old_contract_email(self):
        """ Testa se está tudo ok emails após a criação de um novo contrato
        de parceria  e a edição de um já existente """

        contract = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })

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




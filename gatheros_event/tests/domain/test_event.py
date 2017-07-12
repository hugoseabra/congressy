""" Testes `Event` """
from datetime import datetime, timedelta

from kanu_locations.models import City

from core.tests import GatherosTestCase
from gatheros_event.models import Category, Event, Organization, Place
from gatheros_event.models.rules import event as rule


class EventModelTest(GatherosTestCase):
    """ Testes de `Event` """
    fixtures = [
        'kanu_locations_city_test',
        '004_category',
        '007_organization',
    ]

    def setUp(self):
        self.event = self._create_event(persist=False)
        self.organization = self._create_organization(persist=False)

    def _create_event(self, **kwargs):
        data = {
            "name": 'Event tests',
            "organization": Organization.objects.first(),
            "category": Category.objects.first(),
            "subscription_type": Event.SUBSCRIPTION_DISABLED,
            "date_start": datetime.now(),
            "date_end": datetime.now() + timedelta(hours=8)
        }
        return self._create_model(model_class=Event, data=data, **kwargs)

    def _create_organization(self, **kwargs):
        data = {"name": 'Org test'}
        return self._create_model(
            model_class=Organization,
            data=data,
            **kwargs
        )

    def _create_place(self, organization=None, **kwargs):
        if not organization:
            organization = self._create_organization()

        data = {
            "name": "Modul Coworking",
            "organization": organization,
            "city": City.objects.get(pk=5413),
            "phone": None,
            "long": None,
            "lat": None,
            "zip_code": "74120080",
            "street": "Rua 18, 282",
            "complement": "Galeria Marfim, Sl 7",
            "village": "Setor Oeste",
            "reference": None
        }
        return self._create_model(model_class=Place, data=data, **kwargs)

    def test_rule_1_data_inicial_antes_da_data_final(self):
        rule_callback = rule.rule_1_data_inicial_antes_da_data_final

        self.event.date_start = datetime.now()
        self.event.date_end = datetime.now() - timedelta(days=1)

        """ REGRA """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[self.event],
            field='date_start'
        )

        """ MODEL """
        self._trigger_validation_error(
            callback=self.event.save,
            field='date_start'
        )

    def test_rule_2_local_deve_ser_da_mesma_organizacao_do_evento(self):
        rule_callback = rule. \
            rule_2_local_deve_ser_da_mesma_organizacao_do_evento

        # Adds a place which does not belong to its organization
        self.event.place = self._create_place()

        """ REGRA """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[self.event],
            field='place'
        )

        """ MODEL """
        self._trigger_validation_error(callback=self.event.save, field='place')

    def test_rule_3_evento_data_final_posterior_atual(self):
        rule_callback = rule.rule_3_evento_data_final_posterior_atual

        self.event.date_start = datetime.now() - timedelta(days=2)
        self.event.date_end = datetime.now() - timedelta(days=1)

        """ REGRA """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[self.event, True],
            field='date_end'
        )

        """ MODEL """
        self._trigger_validation_error(
            callback=self.event.save,
            field='date_end'
        )

    def test_rule_4_running_published_event_cannot_change_date_start(self):
        rule_callback = \
            rule.rule_4_running_published_event_cannot_change_date_start

        self.event.date_start = datetime.now() - timedelta(hours=2)
        self.event.date_end = datetime.now() + timedelta(hours=6)
        self.event.published = True
        self.event.save()

        # Mudando data inicial com evento publicado
        self.event.date_start = datetime.now() - timedelta(hours=8)

        # RULE
        self._trigger_validation_error(
            callback=rule_callback,
            params=[self.event],
            field='date_start'
        )

        # MODEL
        self._trigger_validation_error(
            callback=self.event.save,
            field='date_start'
        )

        self.event.published = False
        self.event.date_start = datetime.now() - timedelta(hours=8)

        # RULE
        rule_callback(self.event)

        # MODEL
        self.event.save()

    def test_slug_gerado(self):
        event = self._create_event(persist=True)
        self.assertIsNotNone(event.slug)

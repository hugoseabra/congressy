from datetime import datetime, timedelta

from kanu_locations.models import City

from gatheros_event.lib.test import GatherosTestCase
from gatheros_event.models import Category, Event, Organization, Person
from gatheros_subscription.models import Lot, Subscription
from gatheros_subscription.models.rules import subscription as rule


class SubscriptionModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '005_lot',
        '006_subscription',
    ]

    def _create_person( self, **kwargs ):
        data = {
            'name': 'Test',
            'genre': 'M',
            'city': City.objects.get(pk=5413),
            'cpf': '82247263631'
        }
        return self._create_model(Model=Person, data=data, **kwargs)

    def _create_event( self, **kwargs ):
        data = {
            "name": "Event Test",
            "date_start": datetime.now() + timedelta(days=5),
            "date_end": datetime.now() + timedelta(days=6),
            "organization": Organization.objects.get(pk=5),
            "category": Category.objects.get(pk=4),
            "subscription_type": Event.SUBSCRIPTION_BY_LOTS
        }
        return self._create_model(Model=Event, data=data, **kwargs)

    def _create_lot( self, event=None, **kwargs ):
        if not event:
            event = self._create_event(persist=True)

        data = {
            "name": "Lot Test",
            "event": event,
            "date_start": event.date_start - timedelta(days=8),
            "date_end": event.date_start - timedelta(minutes=3),
            "limit": None,
            "price": None,
            "internal": False
        }

        return self._create_model(Model=Lot, data=data, **kwargs)

    def _create_subscription( self, lot=None, person=None, **kwargs ):
        if not lot:
            lot = self._create_lot(persist=True)

        if not person:
            person = self._create_person(persist=True)

        data = {
            'person': person,
            'lot': lot,
            'origin': Subscription.DEVICE_ORIGIN_WEB,
            'code': None,
            'created_by': 1
        }
        return self._create_model(Model=Subscription, data=data, **kwargs)

    def test_rule_1_limite_lote_excedido( self ):
        rule_callback = rule.rule_1_limite_lote_excedido

        lot = self._create_event(persist=True).lots.first()
        lot.limit = 2

        self._create_subscription(lot=lot, person=self._create_person(cpf='53026113336', persist=True), persist=True)
        self._create_subscription(lot=lot, person=self._create_person(cpf='85221264455', persist=True), persist=True)
        subscription = self._create_subscription(lot=lot)

        """ RULE """
        self._trigger_integrity_error(callback=rule_callback, params=[subscription])

        """ MODEL """
        self._trigger_integrity_error(callback=subscription.save)

        """ FUNCIONANDO """
        lot.limit = 3
        lot.save()
        subscription.save()

    def test_rule_2_codigo_inscricao_deve_ser_gerado( self ):
        rule_callback = rule.rule_2_codigo_inscricao_deve_ser_gerado

        """ RULE """
        subscription = self._create_subscription()
        self.assertIsNone(subscription.code)
        self._trigger_integrity_error(callback=rule_callback, params=[subscription])
        subscription.save()
        rule_callback(subscription)

        """ MODEL | FUNCIONANDO """
        subscription = self._create_subscription(person=self._create_person(cpf='53026113336', persist=True))
        self.assertIsNone(subscription.code)
        subscription.save()
        self.assertIsNotNone(subscription.code)

        subscription.code = None
        subscription.save()
        self.assertIsNotNone(subscription.code)

    def test_rule_3_numero_inscricao_gerado( self ):
        rule_callback = rule.rule_3_numero_inscricao_gerado

        """ RULE """
        subscription = self._create_subscription()
        self.assertIsNone(subscription.count)
        self._trigger_integrity_error(callback=rule_callback, params=[subscription])
        subscription.save()
        rule_callback(subscription)

        """ MODEL | FUNCIONANDO """
        subscription = self._create_subscription(person=self._create_person(cpf='53026113336', persist=True))
        self.assertIsNone(subscription.count)
        subscription.save()
        self.assertIsNotNone(subscription.count)

        subscription.code = None
        subscription.save()
        self.assertIsNotNone(subscription.count)

    def test_rule_4_inscricao_confirmada_com_data_confirmacao( self ):
        rule_callback = rule.rule_4_inscricao_confirmada_com_data_confirmacao

        """ RULE | MODEL | FUNCIONANDO """
        subscription = self._create_subscription()
        self.assertFalse(subscription.attended)
        self.assertIsNone(subscription.attended_on)

        subscription.attended = True
        self._trigger_integrity_error(callback=rule_callback, params=[subscription])

        subscription.attended = False
        subscription.attended_on = datetime.now()
        self._trigger_integrity_error(callback=rule_callback, params=[subscription])

        subscription.attended = True
        subscription.save()
        self.assertIsNotNone(subscription.attended_on)

        rule_callback(subscription)

        subscription.attended = True
        subscription.attended_on = None
        subscription.save()

        self.assertIsNotNone(subscription.attended_on)

        subscription.attended = False
        subscription.save()
        self.assertFalse(subscription.attended)
        self.assertIsNone(subscription.attended_on)

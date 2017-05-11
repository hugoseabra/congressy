from datetime import datetime, timedelta

from core.tests import GatherosTestCase
from gatheros_event.models import Category, Event, Organization
from gatheros_subscription.models import Lot
from gatheros_subscription.models.rules import lot as rule


class LotModelTest(GatherosTestCase):
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
    ]

    def setUp(self):
        self.event_data = {
            "name": "Event Test",
            "organization": Organization.objects.get(pk=5),
            "category": Category.objects.get(pk=4),
            "subscription_type": Event.SUBSCRIPTION_BY_LOTS,
            "subscription_offline": True,
            "date_start": datetime.now() + timedelta(days=1),
            "date_end": datetime.now() + timedelta(days=1, hours=8)
        }
        self.lot_data = {
            "name": "Lot Test",
            "limit": None,
            "price": None,
            "private": False,
            "internal": False
        }

    def _create_event(self, **kwargs):
        return self._create_model(Model=Event, data=self.event_data, **kwargs)

    def _create_lot(self, event=None, **kwargs):
        if not event:
            event = self._create_event(persist=True)

        self.lot_data.update({
            'event': event,
            'date_start': event.date_start - timedelta(days=10),
        })

        return self._create_model(Model=Lot, data=self.lot_data, **kwargs)

    def test_rule_1_event_inscricao_desativada(self):
        rule_callback = rule.rule_1_event_inscricao_desativada

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_DISABLED,
            persist=True
        )
        lot = self._create_lot(event=event)

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='event'
        )

        """ MODEL """
        self._trigger_validation_error(callback=lot.save, field='event')

        """ FUNCIONANDO """
        lot.event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        lot.event.save()
        lot.save()

    def test_rule_2_mais_de_1_lote_evento_inscricao_simples(self):
        rule_callback = rule.rule_2_mais_de_1_lote_evento_inscricao_simples

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_SIMPLE,
            persist=True
        )
        lot = self._create_lot(event=event)

        """ RULE """
        self._trigger_integrity_error(callback=rule_callback, params=[lot])

        """ MODEL """
        self._trigger_integrity_error(callback=lot.save)

        """ FUNCIONANDO """
        lot.event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        lot.event.save()
        lot.save()

    def test_rule_3_evento_inscricao_simples_nao_pode_ter_lot_externo(self):
        rule_callback = \
            rule.rule_3_evento_inscricao_simples_nao_pode_ter_lot_externo

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_SIMPLE,
            persist=True
        )
        lot = event.lots.first()
        lot.internal = False

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='internal'
        )

        """ MODEL """
        self._trigger_validation_error(callback=lot.save, field='internal')

        """ FUNCIONANDO """
        lot.event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        lot.event.save()
        lot.save()

    def test_rule_4_evento_inscricao_por_lotes_nao_ter_lot_interno(self):
        rule_callback = \
            rule.rule_4_evento_inscricao_por_lotes_nao_ter_lot_interno

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS,
            persist=True
        )
        lot = event.lots.first()
        lot.internal = True

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='internal'
        )

        """ MODEL """
        self._trigger_validation_error(callback=lot.save, field='internal')

        """ FUNCIONANDO """
        # Ao mudar tipo, o único lote que sobra é interno
        lot.event.subscription_type = Event.SUBSCRIPTION_SIMPLE
        lot.event.save()
        self.assertTrue(event.lots.first().internal)

    def test_rule_5_data_inicial_antes_data_final(self):
        rule_callback = rule.rule_5_data_inicial_antes_data_final

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS,
            persist=True
        )
        lot = event.lots.first()
        lot.date_start = lot.date_end + timedelta(hours=1)

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='date_start'
        )

        """ MODEL """
        self._trigger_validation_error(
            callback=lot.save,
            field='date_start'
        )

        """ FUNCIONANDO """
        lot.date_start = lot.date_end - timedelta(hours=8)
        lot.save()

    def test_rule_6_data_inicial_antes_data_inicial_evento(self):
        rule_callback = rule.rule_6_data_inicial_antes_data_inicial_evento

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS,
            persist=True
        )
        lot = event.lots.first()
        lot.date_start = lot.event.date_start + timedelta(hours=1)
        lot.date_end = lot.date_start + timedelta(hours=1)

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='date_start'
        )

        """ MODEL """
        self._trigger_validation_error(callback=lot.save, field='date_start')

        """ FUNCIONANDO """
        lot.date_start = lot.event.date_start - timedelta(days=1)
        lot.date_end = lot.event.date_start - timedelta(minutes=1)
        lot.save()

    def test_rule_7_data_final_antes_data_inicial_evento(self):
        rule_callback = rule.rule_7_data_final_antes_data_inicial_evento

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS,
            persist=True
        )
        lot = event.lots.first()
        lot.date_end = lot.event.date_start + timedelta(hours=1)

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='date_end'
        )

        """ MODEL """
        self._trigger_validation_error(callback=lot.save, field='date_end')

        """ FUNCIONANDO """
        lot.date_end = lot.event.date_start - timedelta(minutes=1)
        lot.save()

    def test_rule_8_lot_interno_nao_pode_ter_preco(self):
        rule_callback = rule.rule_8_lot_interno_nao_pode_ter_preco

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_SIMPLE,
            persist=True
        )
        lot = event.lots.first()
        lot.price = 55.00

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='price'
        )

        """ MODEL """
        self._trigger_validation_error(callback=lot.save, field='price')

        """ FUNCIONANDO """
        lot.price = None
        lot.save()

        lot.event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        lot.event.save()
        lot = event.lots.first()
        lot.price = 55.00
        lot.limit = 100
        lot.save()

    def test_rule_9_lote_pago_deve_ter_limite(self):
        rule_callback = rule.rule_9_lote_pago_deve_ter_limite

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS,
            persist=True
        )
        lot = event.lots.first()
        lot.price = 55.00

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='limit'
        )

        """ MODEL """
        self._trigger_validation_error(callback=lot.save, field='limit')

        """ FUNCIONANDO """
        lot.limit = 100
        lot.save()

    def test_rule_10_lote_privado_deve_ter_codigo_promocional(self):
        rule_callback = rule.rule_10_lote_privado_deve_ter_codigo_promocional

        event = self._create_event(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS,
            persist=True
        )
        lot = event.lots.first()
        lot.private = True

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[lot],
            field='promo_code'
        )

        """ MODEL FUNCIONANDO """
        # Gera código ao salvar como privado
        lot.save()

        # Code has been generated
        self.assertIsNotNone(lot.promo_code)

    def test_rule_11_evento_encerrado_nao_pode_ter_novo(self):
        rule_callback = rule.rule_11_evento_encerrado_nao_pode_ter_novo

        event = Event.objects.get(pk=2)
        lot = self._create_lot(event=event)

        """ RULE """
        self._trigger_integrity_error(
            callback=rule_callback,
            params=[lot, True]
        )

        """ MODEL """
        self._trigger_integrity_error(callback=lot.save)

        """ FUNCIONANDO """
        event.date_end = datetime.now() + timedelta(days=1)
        event.save()

        lot.save()

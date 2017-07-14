from datetime import datetime, timedelta

from core.tests import GatherosTestCase
from gatheros_event.models import Event
from gatheros_subscription.models import Form
from gatheros_subscription.models.rules import form as rule


class FormModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '001_default_field',
        '002_default_field_option',
        '007_organization',
        '009_place',
        '010_event'
    ]

    # noinspection PyMethodMayBeStatic
    def _get_event(self, subscription_type=Event.SUBSCRIPTION_SIMPLE):
        event = Event.objects.filter(
            subscription_type=subscription_type
        ).first()

        event.date_start = datetime.now() - timedelta(days=10)
        event.date_end = datetime.now() + timedelta(days=1)
        event.published = False
        event.save()

        return event

    def _create_form(self, event=None, persist=False):
        if not event:
            event = self._get_event()

        data = {'event': event}
        return self._create_model(model_class=Form, data=data, persist=persist)

    def test_rule_1_form_em_event_inscricao_desativada(self):
        """
        Testa erro ao tentar criar formulário em lote com inscrições
        desativadas.
        """
        rule_callback = rule.rule_1_form_em_event_inscricao_desativada

        event = self._get_event(subscription_type=Event.SUBSCRIPTION_DISABLED)
        form = self._create_form(event=event)

        """ RULE """
        self._trigger_integrity_error(rule_callback, [form])

        """ MODEL """
        self._trigger_integrity_error(form.save)

        """ FUNCIONANDO """
        form.event.subscription_type = Event.SUBSCRIPTION_SIMPLE
        form.event.save()
        form.save()

    def test_rule_2_form_possui_todos_campos_padrao(self):
        rule_callback = rule.rule_2_form_possui_todos_campos_padrao

        event = self._get_event()
        form = self._create_form(event=event, persist=True)

        # No assertion
        rule_callback(form)

        # Remover 1 dos campos padrão.
        field = form.fields.first()
        field.delete()

        # Assertion
        self._trigger_integrity_error(rule_callback, [form])

        # Garante todos os campos novamente
        form.save()

        # No assertion
        rule_callback(form)

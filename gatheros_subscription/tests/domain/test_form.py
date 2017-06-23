from datetime import datetime, timedelta

from core.tests import GatherosTestCase
from gatheros_event.models import Event
from gatheros_subscription.models import Form
from gatheros_subscription.models.rules import form as rule


class FormModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '001_default_field',
        '004_category',
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

        # Error
        # Remover 1 dos campos padrão.
        field = event.form.fields.first()
        field.delete()
        self._trigger_integrity_error(rule_callback, [event.form])

        # Garante todos os campos novamente
        event.form.save()
        rule_callback(event.form)

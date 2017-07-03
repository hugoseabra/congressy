from core.tests import GatherosTestCase
from gatheros_event.models import Event
from gatheros_subscription.models import Answer, Field, Subscription
from gatheros_subscription.models.rules import answer as rule


class AnswerModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
        '005_field_option',
        '006_lot',
        '007_subscription',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_field(self):
        return Field.objects.filter(
            form_default_field=False,
            field_type=Field.FIELD_INPUT_TEXT
        ).first()

    # noinspection PyMethodMayBeStatic
    def _get_subscription(self, event):
        return Subscription.objects.filter(event=event).first()

    def _create_answer(self, field=None, subscription=None, **kwargs):
        if not field:
            field = self._get_field()

        if not subscription:
            subscription = self._get_subscription(event=field.form.event)

        data = {
            'field': field,
            'subscription': subscription,
            'value': '{"output": "Teste", "value": "test"}'
        }
        return self._create_model(model_class=Answer, data=data, **kwargs)

    def test_rule_1_mesma_organizacao(self):
        rule_callback = rule.rule_1_mesma_organizacao

        event1 = Event.objects.get(slug='django-muito-alem-do-python')
        field = event1.form.fields.filter(
            form_default_field=False,
            field_type=Field.FIELD_SELECT,
        ).first()

        # Evento diferente que não é da mesma organização do evento anterior
        event2 = Event.objects.get(slug='seo-e-resultados')
        subscription = Subscription.objects.filter(event=event2).first()

        answer = self._create_answer(
            field=field,
            subscription=subscription,
        )

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[answer],
            field='field'
        )

        """ MODEL """
        self._trigger_validation_error(callback=answer.save, field='field')

        """ FUNCIONANDO """
        answer.subscription = Subscription.objects.filter(event=event1).first()
        answer.save()

    def test_rule_2_resposta_apenas_se_campo_adicional(self):
        rule_callback = rule.rule_2_resposta_apenas_se_campo_adicional

        event = Event.objects.get(pk=1)
        field = event.form.fields.filter(form_default_field=True).first()
        subscription = Subscription.objects.filter(event=event).first()

        answer = self._create_answer(field=field, subscription=subscription)

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[answer],
            field='field'
        )

        """ MODEL """
        self._trigger_validation_error(callback=answer.save, field='field')

        """ FUNCIONANDO """
        field.form_default_field = False
        field.save()
        answer.save()

    def test_rule_3_resposta_com_tipo_correto(self):
        rule_callback = rule.rule_3_resposta_com_tipo_correto

        def check_value_type_as_list(field_type):
            event = Event.objects.get(pk=1)
            field = event.form.fields.filter(
                form_default_field=False,
                field_type=field_type
            ).first()

            subscription = Subscription.objects.filter(event=event).first()
            answer = self._create_answer(
                field=field,
                subscription=subscription
            )

            """ RULE """
            self._trigger_validation_error(
                callback=rule_callback,
                params=[answer],
                field='value'
            )

            """ MODEL """
            self._trigger_validation_error(callback=answer.save, field='value')

            """ FUNCIONANDO """
            field.field_type = Field.FIELD_RADIO_GROUP
            field.save()
            answer.save()

        def check_value_type_as_string(field_type):
            event = Event.objects.get(pk=2)
            field = event.form.fields.filter(
                form_default_field=False,
                field_type=field_type
            ).first()

            subscription = Subscription.objects.filter(event=event).first()
            answer = self._create_answer(
                field=field,
                subscription=subscription
            )
            answer.value = '{"value": ["A", "B"]}'

            """ RULE """
            self._trigger_validation_error(
                callback=rule_callback,
                params=[answer],
                field='value'
            )

            """ MODEL """
            self._trigger_validation_error(callback=answer.save, field='value')

            """ FUNCIONANDO """
            field.field_type = Field.FIELD_CHECKBOX_GROUP
            field.save()
            answer.save()

        check_value_type_as_list(Field.FIELD_CHECKBOX_GROUP)
        check_value_type_as_string(Field.FIELD_INPUT_TEXT)

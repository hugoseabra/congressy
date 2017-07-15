from datetime import datetime, timedelta

from core.tests import GatherosTestCase
from gatheros_event.models import Event
from gatheros_subscription.models import Form, Field
from gatheros_subscription.models.rules import form as rule


class FormModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '001_default_field',
        '002_default_field_option',
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_event(
            self,
            slug=None,
            subscription_type=Event.SUBSCRIPTION_SIMPLE
    ):
        if not slug:
            event = Event.objects.filter(
                subscription_type=subscription_type
            ).first()
        else:
            event = Event.objects.get(slug=slug)

        event.date_start = datetime.now() - timedelta(days=10)
        event.date_end = datetime.now() + timedelta(days=1)
        event.published = False
        event.save()

        return event

    def _create_form(self, event=None, persist=False):
        if not event:
            event = self._get_event()

        if hasattr(event, 'form') and event.form is not None:
            return event.form

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

    def test_has_additional_fields(self):
        """ Testa resposta se formulário possui campos adicionais. """
        event = self._get_event(slug='django-muito-alem-do-python')

        add_fields = event.form.fields.filter(form_default_field=False)
        self.assertTrue(add_fields.count() > 0)
        self.assertTrue(event.form.has_additional_fields())

    def test_get_additional_fields(self):
        """ Testa resgate de apenas campos adicionais. """
        event = self._get_event(slug='django-muito-alem-do-python')

        add_fields = event.form.fields.filter(form_default_field=False)
        self.assertTrue(add_fields.count() > 0)

        add_field_pks = [f.pk for f in add_fields]

        for field in event.form.get_additional_fields():
            self.assertIn(field.pk, add_field_pks)

    def test_field_is_required(self):
        """
        Testa verificação se campo no formulário é obrigatório, baseado nas
        configurações de obrigatoriedade.
        """
        event = self._get_event(slug='django-muito-alem-do-python')

        form = event.form
        form.required_configuration = None
        form.save()

        field = form.fields.filter(
            form_default_field=False,
            required=True
        ).first()

        # Testa se obrigatório a partir do original do campo
        self.assertTrue(field.required)
        self.assertTrue(form.is_required(field))

        # Testa se não-obrigatório a partir do original do campo
        field.required = False
        field.save()
        self.assertFalse(field.required)
        self.assertFalse(form.is_required(field))

        # Configura campo como obrigatório neste formulário
        form.required_configuration = {field.name: True}
        form.save()

        # Testa como obrigatório mesmo o campo sendo não-obrigatório por padrão
        self.assertFalse(field.required)
        self.assertTrue(form.is_required(field))

        # Inverte campo como obrigatório
        field.required = True
        field.save()

        form.required_configuration = {field.name: False}
        form.save()

        # Testa como não-obrigatório mesmo o campo sendo obrigatório por padrão
        self.assertTrue(field.required)
        self.assertFalse(form.is_required(field))

    def test_get_field_order(self):
        """
        Testa resgate de lista de ordem de campos e o número da ordenação.
        """
        event = self._get_event(slug='django-muito-alem-do-python')
        form = event.form
        order_list = form.get_order_list()

        for index, field_name in enumerate(order_list):
            field = form.fields.get(name=field_name)
            self.assertEqual(index, form.get_field_order(field))

    def test_add_to_order(self):
        """
        Testa adição de novo campo e se ordem do campo está ao final da
        ordenação.
        """
        event = self._get_event(slug='django-muito-alem-do-python')
        form = event.form
        order_list = form.get_order_list()
        last_field = form.fields.get(name=order_list[-1])
        last_order = form.get_field_order(last_field)

        new_field = Field.objects.create(
            label='New field',
            organization=event.organization
        )
        event.organization.fields.add(new_field)
        event.organization.save()

        form.fields.add(new_field)

        self.assertEqual(form.get_field_order(new_field), last_order + 1)

    def test_inactivate_field(self):
        """
        Testa verificação se campo no formulário é inativo, baseado nas
        configurações inatividade de campos.
        """
        event = self._get_event(slug='django-muito-alem-do-python')
        form = event.form
        field = form.fields.first()

        inactive_list = form.get_inactive_fields_list()
        self.assertNotIn(field.name, inactive_list)
        self.assertTrue(form.is_active(field))

        form.deactivate_field(field)
        form.save()

        inactive_list = form.get_inactive_fields_list()
        self.assertIn(field.name, inactive_list)
        self.assertFalse(form.is_active(field))

    def test_activate_field(self):
        """ Testa mudança de um campo anteriormente inativo para ativo. """
        event = self._get_event(slug='django-muito-alem-do-python')
        form = event.form
        field = form.fields.first()

        form.deactivate_field(field)
        form.save()
        self.assertFalse(form.is_active(field))

        form.activate_field(field)
        form.save()
        self.assertTrue(form.is_active(field))

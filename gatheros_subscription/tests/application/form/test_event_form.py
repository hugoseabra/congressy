from django.core.exceptions import PermissionDenied
from django.test import TestCase

from gatheros_event.models import Event, Organization
from gatheros_subscription.forms import (
    EventFieldsForm,
    FormFieldForm,
    FormFieldOrderForm
)
from gatheros_subscription.models import Field

FIXTURES = [
    '007_organization',
    '009_place',
    '010_event',
    '003_form',
    '004_field',
    '005_field_option',
]


class EventFieldsFormRenderTest(TestCase):
    """ Testa exibição de formulário com campos de um evento. """
    fixtures = FIXTURES

    def setUp(self):
        organization = Organization.objects.get(slug='diego-tolentino')
        self.form = organization.events.first().form

    def test_render_only_active(self):
        """
        Testa se formulário renderiza apenas campos ativos.
        """
        last_field = self.form.fields.last()
        last_field.active = False
        last_field.save()

        form = EventFieldsForm(form=self.form)
        content = form.as_ul()

        fields = self.form.fields.filter(active=True)
        for field in fields:
            self.assertIn(field.name, content)

        self.assertNotIn(last_field.name, content)

    def test_render_all_fields(self):
        """
        Testa se formulário possui todos os formulários.
        """
        last_field = self.form.fields.last()
        last_field.active = False
        last_field.save()

        form = EventFieldsForm(form=self.form, show_inactive=True)
        content = form.as_ul()

        fields = self.form.fields.all()
        for field in fields:
            self.assertIn(field.name, content)


class FormFieldFormTest(TestCase):
    """ Testa formulário que relaciona formulário de evento com campos. """
    fixtures = FIXTURES

    def setUp(self):
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.event = self.organization.events.filter(
            subscription_type=Event.SUBSCRIPTION_SIMPLE
        ).first()
        self.form = FormFieldForm(form=self.event.form)

    def test_field_restriction(self):
        """ Testa restrição de manipulação de `Field`. """
        default_field = self.organization.fields.filter(
            form_default_field=True
        ).first()

        with self.assertRaises(PermissionDenied) as e:
            self.form.add_field(default_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

        inactive_field = self.organization.fields.filter(
            form_default_field=False
        ).last()
        inactive_field.active = False
        inactive_field.save()

        with self.assertRaises(PermissionDenied) as e:
            self.form.add_field(inactive_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

        other_org = Organization.objects.exclude(
            pk=self.organization.pk
        ).filter(internal=False).first()
        other_form = other_org.events.exclude(form__isnull=True).first().form
        other_org_field = other_form.fields.last()

        with self.assertRaises(PermissionDenied) as e:
            self.form.add_field(other_org_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

    def test_add_field(self):
        """ Testa adição de campo no formulário de evento. """
        data = {
            'organization': self.organization,
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': 'New one',
        }

        field = Field.objects.create(**data)
        self.form.add_field(field)

        field_names = [field.name for field in self.event.form.fields.all()]
        self.assertIn(field.name, field_names)

    def test_add_in_last_order(self):
        """ Testa se campo adicionando entra na última posição a ordenação. """
        data = {
            'organization': self.organization,
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': 'New one',
        }

        field = Field.objects.create(**data)
        self.form.add_field(field)

        order = self.event.form.get_order_list()
        last_field = order[-1]
        self.assertEqual(field.name, last_field)

    def test_add_changing_original_required(self):
        """
        Testa adição de campo mudando o valor de `required` especificamente
        para o formulário do evento.
        """

        # Mantendo required original
        original_data = {
            'organization': self.organization,
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': 'New one',
        }

        data = original_data
        data.update({
            'required': True
        })
        field = Field.objects.create(**data)
        self.form.add_field(field)

        config = self.event.form.required_configuration
        self.assertNotIn(field.name, config if config else {})
        self.assertTrue(self.event.form.is_required(field))

        # Inversão: True por padrão e False para o formulário
        data = original_data
        data.update({
            'required': True
        })
        field = Field.objects.create(**data)
        self.form.add_field(field, required=False)

        config = self.event.form.required_configuration
        self.assertIn(field.name, config)
        self.assertFalse(self.event.form.is_required(field))

        # Inversão: False por padrão e True para o formulário
        data = original_data
        data.update({
            'required': False
        })
        field = Field.objects.create(**data)
        self.form.add_field(field, required=True)

        config = self.event.form.required_configuration
        self.assertIn(field.name, config)
        self.assertTrue(self.event.form.is_required(field))

    def test_add_new(self):
        """ Testa criação e adição de novo campo. """
        data = {
            'organization': self.organization,
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': 'New one',
            'required': True,
            'active': True
        }
        field = self.form.add_new_field(data)

        field_names = [field.name for field in self.event.form.fields.all()]
        self.assertIn(field.name, field_names)

    def test_deactivate_field(self):
        """ Testa desativação de campo ativo no formulário. """
        field = self.event.form.fields.last()
        self.form.deactivate(field)

        inactive_fields = self.event.form.get_inactive_field_list()
        self.assertIn(field.name, inactive_fields)

    def test_activate_field(self):
        """ Testa ativação de campo inativo no formulário. """
        field = self.event.form.fields.last()
        self.form.deactivate(field)

        self.form.activate(field)
        inactive_fields = self.event.form.get_inactive_field_list()
        self.assertNotIn(field.name, inactive_fields)


class FormFieldOrderFormTest(TestCase):
    """ Testa reordenação de campos no formulário. """
    fixtures = FIXTURES

    def setUp(self):
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.event = self.organization.events.filter(
            subscription_type=Event.SUBSCRIPTION_SIMPLE
        ).first()
        self.form = self.event.form
        self.order_form = FormFieldOrderForm(form=self.form)

    def test_field_restriction(self):
        """ Testa restrição de manipulação de `Field`. """
        default_field = self.organization.fields.filter(
            form_default_field=True
        ).first()

        with self.assertRaises(PermissionDenied) as e:
            self.order_form.order_up(default_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

        with self.assertRaises(PermissionDenied) as e:
            self.order_form.order_down(default_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

        inactive_field = self.organization.fields.filter(
            form_default_field=False
        ).last()
        inactive_field.active = False
        inactive_field.save()

        with self.assertRaises(PermissionDenied) as e:
            self.order_form.order_up(inactive_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

        with self.assertRaises(PermissionDenied) as e:
            self.order_form.order_down(inactive_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

        other_org = Organization.objects.exclude(
            pk=self.organization.pk
        ).filter(internal=False).first()
        other_form = other_org.events.exclude(form__isnull=True).first().form
        other_org_field = other_form.fields.last()

        with self.assertRaises(PermissionDenied) as e:
            self.order_form.order_up(other_org_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

        with self.assertRaises(PermissionDenied) as e:
            self.order_form.order_down(other_org_field)
            self.assertEqual(str(e), 'Este campo não pode ser adicionado')

    def test_order_down(self):
        """
        Testa reposicionamento de campo para uma posição anterior a atual.
        """

        def get_field_by_order(order):
            order_list = self.form.get_order_list()
            return self.form.fields.get(name=order_list[order])

        position = 6
        field = get_field_by_order(position)
        self.order_form.order_down(field)

        field_reordered = get_field_by_order(position - 1)

        self.assertEqual(field.name, field_reordered.name)

    def test_order_up(self):
        """
        Testa reposicionamento de campo para uma posição posterior a atual.
        """

        def get_field_by_order(order):
            order_list = self.form.get_order_list()
            return self.form.fields.get(name=order_list[order])

        position = 6
        field = get_field_by_order(position)
        self.order_form.order_up(field)

        field_reordered = get_field_by_order(position + 1)

        self.assertEqual(field.name, field_reordered.name)

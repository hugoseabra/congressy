from django.core.exceptions import ValidationError
from django.test import TestCase

from gatheros_event.models import Event
from gatheros_subscription.forms import (
    EventConfigForm,
    EventFormFieldForm,
    EventFormFieldOrderForm,
)
from gatheros_subscription.models import Field


class EventConfigFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
        '005_field_option',
    ]

    def setUp(self):
        self.event = Event.objects.get(slug='arte-e-agricultura-urbana')

    def test_render(self):
        """
        Testa se formulário possui todos os campos do formulário de evento
        """
        entity_form = self.event.form
        form = EventConfigForm(form=entity_form)
        content = form.as_ul()

        for field in entity_form.fields.all():
            self.assertIn(field.name, content)
            self.assertIn(field.label.title(), content)


class EventFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
        '005_field_option',
    ]

    def setUp(self):
        self.event = Event.objects.get(slug='arte-e-agricultura-urbana')

    def _get_form(self, instance=None, data=None):
        return EventFormFieldForm(
            form=self.event.form,
            instance=instance,
            data=data
        )

    def test_raises_wrong_form(self):
        """
        Testa se ValidationError quando formulário que não seja do evento está
        para ser editado.
        """
        event = Event.objects.get(slug='django-muito-alem-do-python')
        field = self.event.form.fields.filter(form_default_field=False).first()

        with self.assertRaises(ValidationError) as e:
            EventFormFieldForm(
                form=event.form,
                instance=field,
            )

        self.assertIn(
            'Este campo não pertence ao formulário `Django, muito além do'
            ' Python`',
            str(e.exception)
        )

    def test_add(self):
        """ Testa adicionado um novo campo. """
        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'name': 'New Field',
            'label': 'New Field',
            'active': True
        }

        form = self._get_form(data=data)
        if not form.is_valid():
            print(form.errors)

        self.assertTrue(form.is_valid())
        saved = form.save()

        field = Field.objects.get(pk=saved.pk)
        self.assertEqual(field.pk, saved.pk)

    def test_raises_edit_default_field(self):
        """ Testa ValidationError se campo é padrão. """
        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'name': 'New Field',
            'label': 'New Field',
            'active': True
        }
        field = self.event.form.fields.filter(form_default_field=True).first()

        with self.assertRaises(ValidationError) as e:
            self._get_form(instance=field, data=data)

        self.assertIn('Este campo não pode ser editado', str(e.exception))

    def test_edit(self):
        """ Testa edição de campo. """

        field = self.event.form.fields.filter(
            form_default_field=False,
            field_type=Field.FIELD_BOOLEAN,
            active=True
        ).first()

        data = {
            'field_type': Field.FIELD_TEXTAREA,
            'name': field.name + ' edited',
            'label': field.name + ' edited',
            'active': False
        }

        form = self._get_form(instance=field, data=data)

        if not form.is_valid():
            print(form.errors)

        self.assertTrue(form.is_valid())
        form.save()

        field = Field.objects.get(pk=field.pk)
        self.assertEqual(field.field_type, data['field_type'])
        self.assertFalse(field.active)


class EventFormFieldOrderFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
        '005_field_option',
    ]

    def setUp(self):
        self.event = Event.objects.get(slug='arte-e-agricultura-urbana')

    def test_get_previous_field(self):
        """ Testa captura de campo anterior. """

        first_field = self.event.form.fields.last()

        form = EventFormFieldOrderForm(instance=first_field)
        previous = form.get_previous_field(first_field.order)

        self.assertEqual(previous.order, first_field.order - 1)

    def test_get_next_field(self):
        """ Testa captura de próximo campo. """
        first_field = self.event.form.fields.filter(
            form_default_field=False
        ).first()

        form = EventFormFieldOrderForm(instance=first_field)
        next_field = form.get_next_field(first_field.order)

        self.assertEqual(next_field.order, first_field.order + 1)

    def test_get_previous_when_first(self):
        """ Testa captura de campo anterior vazio se primeiro campo. """

        first_field = self.event.form.fields.first()
        form = EventFormFieldOrderForm(instance=first_field)
        previous = form.get_previous_field(first_field.order)
        self.assertIsNone(previous)

    def test_get_previous_when_last(self):
        """ Testa captura de próximo campo vazio se último campo. """

        first_field = self.event.form.fields.last()
        form = EventFormFieldOrderForm(instance=first_field)
        next_field = form.get_next_field(first_field.order)
        self.assertIsNone(next_field)

    def test_order_down(self):
        """ Testa reordenação de campo para baixo. """

        first_field = self.event.form.fields.last()
        first_field_order = first_field.order

        form = EventFormFieldOrderForm(instance=first_field)

        previous_field = form.get_previous_field(first_field.order)
        saved_field = form.order_down()

        # Primeiro campo assume ordem do campo anterior
        self.assertEqual(saved_field.order, previous_field.order)

        # Campo prévio agora como próximo
        same_previous_field = Field.objects.get(pk=previous_field.pk)

        # Ordem deve ser igual a primeiro campo
        self.assertEqual(same_previous_field.order, first_field_order)

    def test_order_up(self):
        """ Testa reordenação de campo para baixo. """

        first_field = self.event.form.fields.filter(
            form_default_field=False
        ).first()
        first_field_order = first_field.order

        form = EventFormFieldOrderForm(instance=first_field)

        next_field = form.get_next_field(first_field.order)
        saved_field = form.order_up()

        # Primeiro campo assume ordem do próximo campo
        self.assertEqual(saved_field.order, next_field.order)

        # Próximo campo agora como anterior
        same_next_field = Field.objects.get(pk=next_field.pk)

        # Ordem deve ser igual a primeiro campo
        self.assertEqual(same_next_field.order, first_field_order)

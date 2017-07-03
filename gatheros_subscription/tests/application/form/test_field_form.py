from django.core.exceptions import PermissionDenied
from django.test import TestCase

from gatheros_event.models import Event, Organization
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


class EventFieldTest(TestCase):
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
        Testa se PermissionDenied se campo editado é da mesma organização do
        evento do formulário.
        """
        event = Event.objects.get(slug='django-muito-alem-do-python')
        field = self.event.form.fields.filter(form_default_field=False).first()

        other_org = Organization.objects.exclude(
            pk=event.organization.pk
        ).filter(events__subscription_type=Event.SUBSCRIPTION_BY_LOTS).first()
        other_event = other_org.events.first()

        with self.assertRaises(PermissionDenied) as e:
            EventFormFieldForm(
                form=other_event.form,
                instance=field,
            )

        self.assertIn(
            'Este campo não pertence a organização do evento',
            str(e.exception)
        )

    def test_add(self):
        """ Testa adicionado um novo campo. """
        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'name': 'New Field',
            'label': 'New Field',
            'active': True,
            'organization': self.event.organization
        }

        form = self._get_form(data=data)
        if not form.is_valid():
            print(form.errors)

        self.assertTrue(form.is_valid())
        saved = form.save()

        field = Field.objects.get(pk=saved.pk)
        self.assertEqual(field.pk, saved.pk)

    # def test_new_field_always_last_one(self):
    #     form = Form.objects.first()
    #     last_order = form.fields.order_by('-order').first().order
    #
    #     field = self._create_field(form=form, persist=True)
    #
    #     self.assertEqual(field.order, last_order + 1)

    def test_raises_edit_default_field(self):
        """ Testa ValidationError se campo é padrão. """
        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'name': 'New Field',
            'label': 'New Field',
            'active': True,
            'organization': self.event.organization
        }
        field = self.event.form.fields.filter(form_default_field=True).first()

        with self.assertRaises(PermissionDenied) as e:
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


class EventFieldFieldOrderFormTest(TestCase):
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

        form = self.event.form
        first_field = form.fields.last()

        form = EventFormFieldOrderForm(form=form, instance=first_field)
        previous = form.get_previous_field(first_field.order)

        self.assertEqual(previous.order, first_field.order - 1)

    def test_order_wrong_field(self):
        """
        Testa ordenação de formulário e campo que são de organizações
        diferentes.
        """
        form = self.event.form
        first_field = form.fields.filter(
            form_default_field=False
        ).first()

        other_org = Organization.objects.exclude(
            pk=self.event.organization.pk
        ).filter(events__subscription_type=Event.SUBSCRIPTION_BY_LOTS).first()
        other_event = other_org.events.first()

        with self.assertRaises(PermissionDenied) as e:
            EventFormFieldOrderForm(
                form=other_event.form,
                instance=first_field
            )

        self.assertIn(
            'Este campo não pertence a organização do'
            ' evento.', str(e.exception)
        )

    def test_get_next_field(self):
        """ Testa captura de próximo campo. """
        form = self.event.form
        first_field = form.fields.filter(
            form_default_field=False
        ).first()

        form = EventFormFieldOrderForm(form=form, instance=first_field)
        next_field = form.get_next_field(first_field.order)

        self.assertEqual(next_field.order, first_field.order + 1)

    def test_get_previous_when_first(self):
        """ Testa captura de campo anterior vazio se primeiro campo. """

        form = self.event.form
        first_field = form.fields.first()
        form = EventFormFieldOrderForm(form=form, instance=first_field)
        previous = form.get_previous_field(first_field.order)
        self.assertIsNone(previous)

    def test_get_previous_when_last(self):
        """ Testa captura de próximo campo vazio se último campo. """

        form = self.event.form
        first_field = form.fields.last()
        form = EventFormFieldOrderForm(form=form, instance=first_field)
        next_field = form.get_next_field(first_field.order)
        self.assertIsNone(next_field)

    def test_order_down(self):
        """ Testa reordenação decrescente de campo. """

        form = self.event.form
        first_field = form.fields.last()
        first_field_order = first_field.order

        form = EventFormFieldOrderForm(form=form, instance=first_field)

        previous_field = form.get_previous_field(first_field.order)
        saved_field = form.order_down()

        # Primeiro campo assume ordem do campo anterior
        self.assertEqual(saved_field.order, previous_field.order)

        # Campo prévio agora como próximo
        same_previous_field = Field.objects.get(pk=previous_field.pk)

        # Ordem deve ser igual a primeiro campo
        self.assertEqual(same_previous_field.order, first_field_order)

    def test_order_up(self):
        """ Testa reordenação crescente de campo. """

        form = self.event.form
        first_field = form.fields.filter(
            form_default_field=False
        ).first()
        first_field_order = first_field.order

        form = EventFormFieldOrderForm(form=form, instance=first_field)

        next_field = form.get_next_field(first_field.order)
        saved_field = form.order_up()

        # Primeiro campo assume ordem do próximo campo
        self.assertEqual(saved_field.order, next_field.order)

        # Próximo campo agora como anterior
        same_next_field = Field.objects.get(pk=next_field.pk)

        # Ordem deve ser igual a primeiro campo
        self.assertEqual(same_next_field.order, first_field_order)

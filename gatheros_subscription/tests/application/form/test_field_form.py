from django.core.exceptions import PermissionDenied
from django.test import TestCase

from gatheros_event.models import Organization
from gatheros_subscription.forms import (
    FieldForm,
    OrganizationFieldsForm
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


class FieldsFormRenderTest(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.organization = Organization.objects.get(slug='diego-tolentino')

    def test_render(self):
        """
        Testa se formulário possui todos os campos `não-padrão` da organização.
        """
        form = OrganizationFieldsForm(organization=self.organization)
        content = form.as_ul()

        fields = self.organization.fields.filter(form_default_field=False)
        for field in fields:
            self.assertIn(field.name, content)


class FieldFormTest(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.organization = Organization.objects.get(slug='diego-tolentino')

    def _get_form(self, instance=None, data=None):
        return FieldForm(
            organization=self.organization,
            instance=instance,
            data=data
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

    def test_raises_wrong_org(self):
        """
        Testa se PermissionDenied se campo é da mesma organização da instância
        do formulário.
        """
        org = Organization.objects.get(slug='mnt')
        field = self.organization.fields.filter(
            form_default_field=False
        ).first()

        with self.assertRaises(PermissionDenied) as e:
            FieldForm(organization=org, instance=field)

        self.assertIn(
            'Este campo não pertence à organização "{}"'.format(org.name),
            str(e.exception)
        )

    def test_raises_edit_default_field(self):
        """ Testa PermissionDenied se campo é padrão. """
        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'name': 'New Field',
            'label': 'New Field',
            'active': True,
        }
        field = self.organization.fields.filter(
            form_default_field=True
        ).first()

        with self.assertRaises(PermissionDenied) as e:
            self._get_form(instance=field, data=data)

        self.assertIn('Este campo não pode ser editado', str(e.exception))

    def test_edit(self):
        """ Testa edição de campo. """

        field = self.organization.fields.filter(
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

from django.core.exceptions import PermissionDenied
from django.test import TestCase

from gatheros_event.models import Event, Organization
from gatheros_subscription.forms import FieldOptionForm
from gatheros_subscription.models import FieldOption


FIXTURES = [
    '007_organization',
    '009_place',
    '010_event',
    '003_form',
    '004_field',
    '005_field_option',
]


class FieldOptionFormTest(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.organization = Organization.objects.get(slug='diego-tolentino')
        self.field = self.organization.fields.filter(
            form_default_field=False,
            with_options=True
        ).first()

    def _get_form(self, instance=None, data=None):
        return FieldOptionForm(
            field=self.field,
            instance=instance,
            data=data
        )

    def test_add(self):
        """ Testa adicionado um novo campo. """
        data = {'name': 'Opção 1'}

        form = self._get_form(data=data)
        if not form.is_valid():
            print(form.errors)

        self.assertTrue(form.is_valid())
        saved = form.save()

        field = FieldOption.objects.get(pk=saved.pk)
        self.assertEqual(field.pk, saved.pk)

    def test_raises_wrong_org(self):
        """
        Testa se PermissionDenied se opção é da mesma organização da instância
        do formulário.
        """
        # Outra opção qualquer
        option = FieldOption.objects.exclude(field=self.field).first()

        with self.assertRaises(PermissionDenied) as e:
            FieldOptionForm(field=self.field, instance=option)

        self.assertIn('Você não pode editar esta opção', str(e.exception))

    def test_field_default_field(self):
        """ Testa se PermissionDenied se opção é de um campo padrão. """
        field = self.organization.fields.filter(
            form_default_field=True,
            with_options=True
        ).first()

        with self.assertRaises(PermissionDenied) as e:
            FieldOptionForm(field=field)

        self.assertIn('Você não pode editar esta opção', str(e.exception))

    def test_field_no_option_support(self):
        """
        Testa se PermissionDenied se opção é de um campo que não suporta
        opções.
        """
        field = self.organization.fields.filter(
            form_default_field=False,
            with_options=False
        ).first()

        with self.assertRaises(PermissionDenied) as e:
            FieldOptionForm(field=field)

        self.assertIn('Você não pode editar esta opção', str(e.exception))

    def test_edit(self):
        """ Testa edição de opção de campo. """

        option = self.field.options.first()

        data = {'name': option.name + ' edited'}
        form = self._get_form(instance=option, data=data)

        if not form.is_valid():
            print(form.errors)

        self.assertTrue(form.is_valid())
        form.save()

        field = FieldOption.objects.get(pk=option.pk)
        self.assertEqual(field.name, data['name'])

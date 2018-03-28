"""
    Testing the application service mixin.
"""

from django import forms
from django.db import models
from django_fake_model import models as f
from test_plus.test import TestCase

from base.managers import Manager
from base.models import EntityMixin
from base.services import (
    ApplicationService,
    ManagerClassMissingError,
    ManagerWrongTypeError,
)


class MyFakeModel(EntityMixin, f.FakeModel):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()


@MyFakeModel.fake_me
class ApplicationServiceMixinTest(TestCase):
    """ Main test implementation """

    class CorrectModelManager(Manager):
        class Meta:
            model = MyFakeModel
            fields = '__all__'

    class ModelFormManager(forms.ModelForm):
        class Meta:
            model = MyFakeModel
            fields = '__all__'

        def is_valid(self):
            return False

    def setUp(self):
        self.correct_manager = self.CorrectModelManager
        self.model_form_manager = self.ModelFormManager
        self.service_class = ApplicationService

    def test_service_creation(self):
        """
            Testa se é possivel criar uma instancia generica deste.
        """
        correct_service_class = ApplicationService
        correct_service_class.display_fields = None
        correct_service_class.hidden_fields = None
        correct_service_class.manager_class = self.correct_manager

        correct_instance = correct_service_class()

        self.assertIsInstance(correct_instance, ApplicationService)

        self.assertEqual(correct_instance.fields,
                         correct_instance.manager.fields)
        self.assertEqual(correct_instance.initial,
                         correct_instance.manager.initial)

    def test_service_manager_retrieval(self):
        """
            Testa se está buscando corretamente o manager.
        """

        service_class = self.service_class
        service_class.manager_class = self.correct_manager
        service = service_class()

        # Correto
        self.assertIsInstance(service._get_manager(), self.correct_manager)

        # Incorreto
        service.manager_class = self.model_form_manager
        with self.assertRaises(ManagerWrongTypeError) as e:
            service._get_manager()
            self.assertEqual(e.msg, 'Manager inválido')

        service.manager_class = None
        with self.assertRaises(ManagerClassMissingError) as e:
            service._get_manager()
            self.assertEqual(e.msg,
                             'Você deve informar uma class de Manager do '
                             'Model')

    def test_service_is_valid(self):
        service_class = ApplicationService
        service_class.manager_class = self.correct_manager
        service_class.display_fields = None
        service_class.hidden_fields = None

        instance_with_no_data = service_class(
            data={
                'name': None,
                'age': None,
            }
        )
        instance_with_data = service_class(
            data={
                'name': 'Jon Snow',
                'age': 30,
            }
        )

        self.assertTrue(instance_with_data.is_valid())

        self.assertFalse(instance_with_no_data.is_valid())

        # Verifica se o que está faltando é de fato o nome.
        self.assertFalse(instance_with_no_data.is_valid())
        error_dict = instance_with_no_data.errors.as_data()

        self.assertIsInstance(error_dict['name'][0], forms.ValidationError)
        self.assertIsInstance(error_dict['age'][0], forms.ValidationError)

    def test_service_save(self):
        service_class = ApplicationService
        service_class.manager_class = self.correct_manager
        service_class.display_fields = None
        service_class.hidden_fields = None

        name = "Jon Snow"

        instance = service_class(
            data={
                'name': name,
                'age': 30,
            }
        )

        self.assertTrue(instance.is_valid())
        instance.save()

        self.assertEqual(name, MyFakeModel.objects.get(name=name).name)

    def test_service_editing(self):
        service_class = ApplicationService
        service_class.manager_class = self.correct_manager
        service_class.display_fields = None
        service_class.hidden_fields = None

        name = "Jon Snow"

        initial_instance = service_class(
            data={
                'name': name,
                'age': 30,
            }
        )

        self.assertTrue(initial_instance.is_valid())
        initial_instance.save()

        persisted_instance = MyFakeModel.objects.get(name=name)

        self.assertEqual(name, persisted_instance.name)

        new_name = 'Jon Targaryn'

        editing_instance = service_class(
            data={
                'name': new_name,
                'age': 30,
            },
            instance=persisted_instance,
        )

        self.assertTrue(editing_instance.is_valid())
        editing_instance.save()

        self.assertEqual(new_name, MyFakeModel.objects.get(name=new_name).name)

    def test_display_fields(self):
        """
        Testa exibição somente do campo configurado em display fields.

        OBS: Se o campo é 'hidden', não irá exibir o <label>
        """
        service_class = ApplicationService
        service_class.manager_class = self.correct_manager
        service_class.display_fields = None
        service_class.hidden_fields = None

        # Renderização exibindo o campo normalmente
        service = service_class()
        content = str(service)

        self.assertIn('<label for="id_name">', content)
        self.assertIn('<label for="id_age">', content)

        # Renderização somente do campo 'age'
        service_class = ApplicationService
        service_class.manager_class = self.correct_manager
        service_class.display_fields = ('age',)

        service = service_class()
        content = str(service)

        self.assertNotIn('<label for="id_name">', content)
        self.assertIn('<label for="id_age">', content)

        # Renderização somente do campo 'name'
        service_class = ApplicationService
        service_class.manager_class = self.correct_manager
        service_class.display_fields = ('name',)

        service = service_class()
        content = str(service)

        self.assertNotIn('<label for="id_age">', content)
        self.assertIn('<label for="id_name">', content)

    def test_hide_field(self):
        """
        Testa campo como 'hidden' se informado em 'hidden_fields' no início
        da instância.

        OBS: Se o campo é 'hidden', não irá exibir o <label>
        """
        service_class = ApplicationService
        service_class.manager_class = self.correct_manager
        service_class.display_fields = None
        service_class.hidden_fields = None

        # Renderização exibindo o campo normalmente
        service = service_class()
        content = str(service)

        self.assertIn('<label for="id_name">', content)
        self.assertIn('<label for="id_age">', content)

        # Renderização escondendo o campo 'nome'
        service_class = ApplicationService
        service_class.manager_class = self.correct_manager
        service_class.hidden_fields = ('name',)

        service = service_class()
        content = str(service)

        self.assertNotIn('<label for="id_name">', content)
        self.assertIn('<label for="id_age">', content)


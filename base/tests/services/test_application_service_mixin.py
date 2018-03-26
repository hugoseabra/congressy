"""
    Testing the application service mixin.
"""

from django import forms
from django.db import models
from django_fake_model import models as f
from test_plus.test import TestCase

from base.managers import Manager
from base.models import Entity
from base.services import (
    ApplicationServiceMixin,
    ManagerClassMissingError,
    ManagerWrongTypeError,
)


class MyFakeModel(Entity, f.FakeModel):
    name = models.CharField(max_length=100)


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
        self.service_class = ApplicationServiceMixin

    def test_service_creation(self):
        """
            Testa se é possivel criar uma instancia generica deste.
        """
        correct_service_class = ApplicationServiceMixin
        correct_service_class.manager_class = self.correct_manager
        correct_instance = correct_service_class()

        self.assertIsInstance(correct_instance, ApplicationServiceMixin)

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
        service_class = ApplicationServiceMixin
        service_class.manager_class = self.correct_manager

        instance_with_no_data = service_class(
            data={
                'name': None
            }
        )
        instance_with_data = service_class(
            data={
                'name': 'Jon Snow'
            }
        )

        self.assertTrue(instance_with_data.is_valid())

        self.assertFalse(instance_with_no_data.is_valid())

        # Verifica se o que está faltando é de fato o nome.
        self.assertFalse(instance_with_no_data.is_valid())
        error_dict = instance_with_no_data.errors.as_data()
        error_list = list(error_dict)

        self.assertEqual(error_list[0], 'name')
        self.assertIsInstance(error_dict['name'][0], forms.ValidationError)

    def test_service_save(self):
        service_class = ApplicationServiceMixin
        service_class.manager_class = self.correct_manager

        name = "Jon Snow"

        instance = service_class(
            data={
                'name': name
            }
        )

        self.assertTrue(instance.is_valid())
        instance.save()

        self.assertEqual(name, MyFakeModel.objects.get(name=name).name)

    def test_service_editing(self):
        service_class = ApplicationServiceMixin
        service_class.manager_class = self.correct_manager

        name = "Jon Snow"

        initial_instance = service_class(
            data={
                'name': name
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
            },
            instance=persisted_instance,
        )

        self.assertTrue(editing_instance.is_valid())
        editing_instance.save()

        self.assertEqual(new_name, MyFakeModel.objects.get(name=new_name).name)

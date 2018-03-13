"""
    Testing the application service mixin.
"""

from django_fake_model import models as f
from django.db import models
from test_plus.test import TestCase

from survey.managers import Manager
from django import forms


class ApplicationServiceFakeModel(f.FakeModel):
    name = models.CharField(max_length=100)


@ApplicationServiceFakeModel.fake_me
class ApplicationServiceMixinTest(TestCase):
    """ Main test implementation """

    class CorrectModelManager(Manager):
        class Meta:
            model = ApplicationServiceFakeModel
            fields = '__all__'

    class IncorrectModelManager(forms.ModelForm):
        class Meta:
            model = ApplicationServiceFakeModel
            fields = '__all__'

        def is_valid(self):
            return False

    def setUp(self):
        # Create a dummy model which extends the mixin
        self.correct_manager = self.CorrectModelManager
        self.incorrect_manager = self.IncorrectModelManager

    def test_manager_is_valid(self):
        manager = self.correct_manager

        instance_with_data = manager(
            data={
                'name': 'Jon Snow'
            }
        )

        instance_with_no_data = manager(
            data={
                'name': None
            }
        )

        self.assertTrue(instance_with_data.is_valid())

        # Verifica se o que está faltando é de fato o nome.
        self.assertFalse(instance_with_no_data.is_valid())
        error_dict = instance_with_no_data.errors.as_data()
        error_list = list(error_dict)

        self.assertEqual(error_list[0], 'name')
        self.assertIsInstance(error_dict['name'][0], forms.ValidationError)


"""
    Tests para o mixin de Managers
"""

from django import forms
from django.db import models
from django_fake_model import models as f
from test_plus.test import TestCase

from survey.managers.mixins import Manager, EntityTypeError
from survey.models.mixins import Entity


class ManagerFakeEntity(Entity, f.FakeModel):
    name = models.CharField(max_length=100)


class ManagerFakeModel(f.FakeModel):
    name = models.CharField(max_length=100)


@ManagerFakeModel.fake_me
@ManagerFakeEntity.fake_me
class ManagerTest(TestCase):
    """ Implementação do test """

    def test_manager_creation(self):
        """
            Testa a criação de um manager.
        """

        class TestManager(Manager):
            class Meta:
                model = ManagerFakeEntity
                fields = '__all__'

        class TestManagerWithoutEntity(Manager):
            class Meta:
                model = ManagerFakeModel
                fields = '__all__'

        # Correct
        self.assertIsInstance(TestManager(), TestManager)

        # Incorrect
        with self.assertRaises(EntityTypeError):
            TestManagerWithoutEntity()



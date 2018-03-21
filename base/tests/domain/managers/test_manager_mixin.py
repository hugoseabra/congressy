"""
    Tests para o mixin de Managers
"""

from django.db import models
from django_fake_model import models as f
from test_plus.test import TestCase

from base.managers import Manager, EntityTypeError
from base.models import Entity


class FakeEntity(Entity, f.FakeModel):
    name = models.CharField(max_length=100)


class FakeModel(f.FakeModel):
    name = models.CharField(max_length=100)


@FakeEntity.fake_me
@FakeModel.fake_me
class ManagerTest(TestCase):
    """ Implementação do test """

    def test_manager_creation(self):
        """
            Testa a criação de um manager.
        """

        class TestManager(Manager):
            class Meta:
                model = FakeEntity
                fields = '__all__'

        class TestManagerWithoutEntity(Manager):
            class Meta:
                model = FakeModel
                fields = '__all__'

        # Correct
        self.assertIsInstance(TestManager(), TestManager)

        # Incorrect
        with self.assertRaises(EntityTypeError):
            TestManagerWithoutEntity()

    def test_get_model_instance(self):
        """
            Testa recuperação de instância do model configurado no Manager.
        """
        instance = FakeEntity()
        instance.save()

        class TestManager(Manager):
            class Meta:
                model = FakeEntity
                fields = '__all__'

        manager = TestManager()
        fetched_instance = manager.get(pk=instance.pk)

        self.assertIsInstance(fetched_instance, FakeEntity)
        self.assertEqual(fetched_instance, instance)

        with self.assertRaises(FakeEntity.DoesNotExist):
            manager.get(pk=1000)

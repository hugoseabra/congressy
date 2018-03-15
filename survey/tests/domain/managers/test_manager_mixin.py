"""
    Testing the application service mixin.
"""

from django_fake_model import models as f
from django.db import models
from test_plus.test import TestCase

from survey.managers import Manager
from faker import Faker
from django import forms


class ApplicationServiceRelatedModel(f.FakeModel):
    name = models.CharField(max_length=100)


class ApplicationServiceRelatedRequiredModel(f.FakeModel):
    name = models.CharField(max_length=100)


class ApplicationServiceModel(f.FakeModel):
    name = models.CharField(max_length=100)

    extra_field = models.ForeignKey(
        ApplicationServiceRelatedModel,
        null=True,
    )

    extra_required_field = models.ForeignKey(
        ApplicationServiceRelatedRequiredModel
    )


@ApplicationServiceModel.fake_me
@ApplicationServiceRelatedModel.fake_me
@ApplicationServiceRelatedRequiredModel.fake_me
class ApplicationServiceMixinTest(TestCase):
    """ Main test implementation """

    class CorrectModelManager(Manager):
        class Meta:
            model = ApplicationServiceModel
            fields = '__all__'

    class IncorrectModelManager(Manager):
        class Meta:
            model = ApplicationServiceModel
            fields = '__all__'

    class ExcludedModelManager(Manager):
        class Meta:
            model = ApplicationServiceModel
            exclude = (
                'extra_required_field',
            )

        def __init__(self, extra_required_field, **kwargs):
            self.extra_required_field = extra_required_field
            kwargs.update({'extra_required_field': extra_required_field})
            super().__init__(**kwargs)

        def save(self, commit=True):
            self.instance.extra_required_field = self.extra_required_field
            return super().save(commit)

    def setUp(self):
        self.faker = Faker('pt_BR')
        self.correct_manager = self.CorrectModelManager
        self.incorrect_manager = self.IncorrectModelManager
        self.excluded_manager = self.ExcludedModelManager

        self.related_model = ApplicationServiceRelatedModel.objects.create(
            name=self.faker.name()
        )
        self.required_model = \
            ApplicationServiceRelatedRequiredModel.objects.create(
                name=self.faker.name()
            )

    def test_manager_validation(self):
        """
            Valida se o manager respeita as regras do model ao qual ele foi
            criado, além de respeitar as regras de definição do manager.
        """
        manager = self.correct_manager
        excluded_manager = self.excluded_manager

        instance_with_data = manager(
            data={
                'name': 'Jon Snow',
                'extra_field': self.related_model.pk,
                'extra_required_field': self.required_model.pk,
            },
        )

        instance_with_no_data = manager(
            data={
                'name': None,
                'extra_field': None,
                'extra_required_field': None,
            }
        )

        instance_with_excluded_data = excluded_manager(
            data={
                'name': 'Jon Stark',
                'extra_field': self.related_model.pk,

            },
            extra_required_field=self.required_model,
        )

        # Verificando que caso seja passado uma referencia('pk') via kwargs,
        # o manager não irá se construir corretamente.
        # Managers trabalham apenas com instancias e não com referencias('pk')
        with self.assertRaises(TypeError):
            excluded_manager(
                data={
                    'name': 'Jon Snow',
                    'extra_field': self.related_model.pk,

                },
                extra_required_field=self.required_model.pk,
            )

        # Validação das instancias corretas.
        self.assertTrue(instance_with_data.is_valid())
        self.assertTrue(instance_with_excluded_data.is_valid())

        # Verifica os erros
        self.assertFalse(instance_with_no_data.is_valid())
        error_dict = instance_with_no_data.errors.as_data()
        error_list = list(error_dict)

        # Verificando que temos três itens faltando
        self.assertIs(3, len(error_list))

        # Verificando o teor dos erros.
        for _, value in error_dict.items():
            self.assertIsInstance(value[0], forms.ValidationError)
            self.assertEqual(value[0].message, 'This field is required.')

        # Verificando a capacidade de persistencia de managers com exclusões
        instance_with_excluded_data.save()
        ApplicationServiceModel.objects.get(name='Jon Stark')

    # def test_manager_editing(self):
    #     manager = self.correct_manager
    #
    #     name = 'Jon Snow'
    #     new_name = 'Jon Targaryn'
    #
    #     initial_instance = manager(
    #         data={
    #             'name': name,
    #             'extra_field': self.related_model.pk,
    #             'extra_required_field': self.required_model.pk,
    #         }
    #     )
    #
    #     self.assertTrue(initial_instance.is_valid())
    #
    #     initial_instance.save()
    #
    #     persisted_instance = ApplicationServiceModel.objects.get(name=name)
    #
    #     editing_instance = manager(
    #         data={
    #             'name': new_name,
    #             'extra_field': self.related_model.pk,
    #             'extra_required_field': self.required_model.pk,
    #         },
    #         instance=persisted_instance,
    #     )
    #     self.assertTrue(editing_instance.is_valid())
    #     editing_instance.save()
    #
    #     # Validando se for persistido.
    #     checking_persisted_instance = ApplicationServiceModel.objects.get(
    #         pk=persisted_instance.pk)
    #
    #     self.assertEqual(new_name, checking_persisted_instance.name)
    #
    # def test_passing_reference_kwarg(self):
    #     regular_manager = self.correct_manager
    #     excluded_manager = self.excluded_manager
    #
    #     regular_instance = regular_manager(
    #         data={
    #             'name': 'Jon Snow',
    #             'extra_required_field': self.required_model.pk,
    #         },
    #     )
    #
    #     self.assertTrue(regular_instance.is_valid())
    #
    #     excluded_manager(
    #         data={
    #             'name': 'Jon Snow',
    #         },
    #         extra_required_field=self.required_model,
    #     )
    #
    #     with self.assertRaises(TypeError):
    #         excluded_manager(
    #             data={
    #                 'name': 'Jon Snow',
    #             },
    #             extra_required_field=self.required_model.pk,
    #         )

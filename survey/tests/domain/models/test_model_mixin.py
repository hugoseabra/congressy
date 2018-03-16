"""
    Testing the model mixin
"""

from test_plus.test import TestCase

from survey.models.mixins import Entity, RuleInstanceTypeError, \
    RuleIntegrityError
from survey.models.rule_checker import RuleChecker
from django.forms import ValidationError


class EntityTest(TestCase):
    """ Entity test implementation """

    def test_entity_creation(self):
        """
            Tests instantiation of the Entity object.

        """
        self.assertTrue(isinstance(Entity(), Entity))

    def test_entity_creation_with_rules(self):
        """
            Tests instantiation of the Entity object with rules passed.
        """

        class TestChecker(RuleChecker):

            def check(self, entity_instance):
                pass

        class NotAChecker(object):
            pass

        entity = Entity

        # Testing creation with correct rules.
        entity.rule_instances = [
            TestChecker()
        ]

        self.assertTrue(isinstance(entity(), Entity))

        # Testing creation with wrong type of rules.
        wrong_entity = Entity
        wrong_instance = NotAChecker()
        wrong_entity.rule_instances = [
            wrong_instance,
        ]

        with self.assertRaises(RuleInstanceTypeError) as e:
            wrong_entity()
            self.assertEqual(str(e.msg), "<class 'survey.tests.domain.models."
                                         "test_model_mixin.EntityTest."
                                         "test_entity_creation_with_rules."
                                         "<locals>.NotAChecker'>")

    def test_entity_cleaning(self):
        """
            Tests cleaning(validation) of an entity.
        """

        class TestCheckerWithExceptions(RuleChecker):

            def check(self, entity_instance):
                raise RuleIntegrityError('Test error')

        entity_with_errors = Entity

        entity_with_errors.rule_instances = [
            TestCheckerWithExceptions()
        ]

        entity_with_errors = entity_with_errors()

        with self.assertRaises(ValidationError) as e:
            entity_with_errors.clean()
            self.assertEqual(str(e.msg, 'Test error'))

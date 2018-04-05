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

    def test_entity_rule_checkers_validation(self):
        """
            Tests instantiation of the Entity object with rules passed.
        """

        # TESTES FALHANDO
        # Testing creation with wrong type of rule checkers.
        class NotAChecker:
            pass

        wrong_entity = Entity
        wrong_entity.rule_instances = [
            NotAChecker(),
        ]

        with self.assertRaises(RuleInstanceTypeError) as e:
            wrong_entity()

        # TESTES FALHANDO
        # Testing creation with correct rules.
        class TestChecker(RuleChecker):
            def check(self, entity_instance):
                pass

        entity = Entity
        entity.rule_instances = [
            TestChecker()
        ]

        # instance does not raise exception
        entity()

    def test_entity_clean_triggering_rule_error(self):
        """
            Testando se o clean do mixin engatilha o exception dos
            rules.
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
            self.assertEqual(str(e.msg), 'Test error')

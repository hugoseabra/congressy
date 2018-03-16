"""
    Testing the rule checker mixin
"""

from test_plus.test import TestCase

from survey.models.rule_checker import RuleChecker


class RuleCheckerTest(TestCase):
    """ Rule checker test implementation """

    def test_rule_checker_creation(self):
        """
            Tests the creation of a new rule checker
        """

        class TestChecker(RuleChecker):

            def check(self, entity_instance):
                pass

        self.assertIsNotNone(TestChecker())

    def test_rule_checker_incorrect_creation(self):
        """
            Tests the creation of a new rule checker without the abstract
            'check()' method.
        """

        class TestChecker(RuleChecker):
            pass

        with self.assertRaises(TypeError) as e:
            TestChecker()

            self.assertEqual(str(e.msg),
                             "Can't instantiate abstract class TestChecker "
                             "with abstract methods check")

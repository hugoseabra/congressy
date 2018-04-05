"""
    Testing the Option model entity
"""

from test_plus.test import TestCase
from django.db import transaction
from django.db.utils import IntegrityError

from survey.models import Option
from survey.tests import MockFactory


class OptionModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.survey = self.fake_factory.fake_survey()
        self.question = self.fake_factory.fake_question(survey=self.survey)

    def test_option_unique_in_question(self):
        """ Testa se valor de opção é único para o campo na mesma questão. """

        name = 'Option #1'

        option1 = Option(
            question=self.question,
            name=name,
            value='42',
        )

        option2 = Option(
            question=self.question,
            name=name,
            value='42',
        )

        option1.save()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                option2.save()

        self.assertEqual(Option.objects.filter(name=name).count(), 1)

    def test_option_same_name_different_question(self):
        """ Testa se valor de opção é único para o campo mas possivel para
        diferentes questões  """

        name = 'Option #1'

        question1 = self.question
        question2 = self.fake_factory.fake_question(self.survey)

        option1 = Option(
            question=question1,
            name=name,
            value='42',
        )

        option2 = Option(
            question=question2,
            name=name,
            value='42',
        )

        with transaction.atomic():
            option1.save()
            option2.save()

        self.assertEqual(Option.objects.filter(name=name).count(), 2)

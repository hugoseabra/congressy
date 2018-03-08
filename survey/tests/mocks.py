"""
    Mock factory used during tests to create required survey domain objects.
"""

from faker import Faker

from survey.models import Survey, Question, Option
from random import randint


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker('pt_BR')

    def fake_survey(self):

        survey = Survey(
            name=' '.join(self.fake_factory.words(nb=2)),
        )

        survey.save()

        assert survey is not None

        return survey

    def fake_question(self, survey, required=False, complex=False):
        question = Question(
            name=' '.join(self.fake_factory.words(nb=3)),
            is_required=required,
            is_complex=complex,
            survey=survey,
        )

        question.save()

        assert question is not None

        return question

    def fake_option(self, question):

        option = Option(
            name=' '.join(self.fake_factory.words(nb=2)),
            value=str(randint(0, 100)),
            question=question,
        )
        option.save()

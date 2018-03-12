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

    def fake_question(self, survey, type=Question.FIELD_INPUT_TEXT,
                      required=False, active=True):

        name = ' '.join(self.fake_factory.words(nb=3))
        help_text = ' '.join(self.fake_factory.words(nb=6))

        question = Question(
            survey=survey,
            type=type,
            name=name,
            label=name,
            required=required,
            help_text=help_text,
            active=active,
        )

        question.save()

        return question

    def fake_option(self, question):

        option = Option(
            name=' '.join(self.fake_factory.words(nb=2)),
            value=str(randint(0, 100)),
            question=question,
        )
        option.save()

        return option

"""
    Mock factory used during tests to create required survey domain objects.
"""

from django.contrib.auth.models import User, AnonymousUser
from django.db import IntegrityError
from faker import Faker
from random import randint

from gatheros_event.models import Person
from survey.models import Survey, Question, Option, Author, Answer


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker('pt_BR')

    def fake_person(self):
        person = Person(name=self.fake_factory.name())
        first_name = person.name.split(' ')[0]
        user = User.objects.create_user(first_name,
                                        self.fake_factory.free_email(),
                                        '123')
        user.save()
        person.user = user
        person.save()

        assert person is not None

        return person

    def fake_user(self, is_anon=False):

        if is_anon:
            return AnonymousUser()

        first_name = self.fake_factory.name().split(' ')[0]

        try:
            user = User.objects.create_user(first_name,
                                            self.fake_factory.free_email(),
                                            '123')
        except IntegrityError:
            first_name = self.fake_factory.name().split(' ')[0]
            user = User.objects.create_user(first_name,
                                            self.fake_factory.free_email(),
                                            '123')
        return user

    def fake_survey(self):
        return Survey.objects.create(
            name=' '.join(self.fake_factory.words(nb=2)),
        )

    def fake_question(self, survey, type=Question.FIELD_INPUT_TEXT,
                      required=False, active=True):
        name = ' '.join(self.fake_factory.words(nb=3))
        help_text = ' '.join(self.fake_factory.words(nb=6))

        return Question.objects.create(
            survey=survey,
            type=type,
            name=name,
            label=name,
            required=required,
            help_text=help_text,
            active=active,
        )

    def fake_option(self, question):
        return Option.objects.create(
            name=' '.join(self.fake_factory.words(nb=2)),
            value=str(randint(0, 100)),
            question=question,
        )

    def fake_author(self, survey, user=None):
        return Author.objects.create(
            survey=survey,
            user=user,
            name=self.fake_factory.name(),
        )

    def fake_answer(self, question, author, value=None):
        if not value:
            value = self.fake_factory.words(nb=2)

        return Answer.objects.create(
            question=question,
            author=author,
            value=value
        )

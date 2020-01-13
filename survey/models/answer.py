"""
    Answer domain model.
    Resposta de um questionário, referente a uma pergunta a pertecente a um
    Autor.
"""
from django.db import models

from core.model import track_data
from survey.models import Author, Question
from survey.models.mixins import RuleChecker, Entity, RuleIntegrityError


class SameSurveyRule(RuleChecker):
    """ Regra de negócio: pergunta e autor devem ser do mesmo questionário. """

    def check(self):
        if self.question.survey != self.author.survey:
            raise RuleIntegrityError(
                'A pergunta e o autor não pertencem ao mesmo questionário.'
            )


@track_data('question_id', 'author_id', 'value', 'human_display')
class Answer(Entity, models.Model):
    """
        Answer domain model implementation.
    """

    rule_instances = [
        SameSurveyRule,
    ]

    class Meta:
        verbose_name = 'resposta'
        verbose_name_plural = 'respostas'

    def __str__(self):  # pragma: no cover
        return '{}: {} ({})'.format(
            self.question.label,
            self.author.name,
            self.value
        )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='pergunta',
        related_name='answers',
    )

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name='autor',
        related_name='answers',
    )

    value = models.TextField(
        verbose_name='valor'
    )

    human_display = models.TextField(
        verbose_name='nome exibido a humanos',
        blank=True,
        null=True,
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em'
    )

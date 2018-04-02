"""
    Answer domain model.
    Resposta de um questionário, referente a uma pergunta a pertecente a um
    Autor.
"""
from django.db import models

from survey.models import Author, Question
from survey.models.mixins import RuleChecker, Entity, RuleIntegrityError


class SameSurveyRule(RuleChecker):
    """ Regra de negócio: pergunta e autor devem ser do mesmo questionário. """

    def check(self):
        if self.question.survey != self.author.survey:
            raise RuleIntegrityError(
                'A pergunta e o autor não pertencem ao mesmo '
                'questionário.'
            )


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

    human_display = models.CharField(
        max_length=255,
        verbose_name='nome exibido a humanos',
        blank=True,
        null=True,
    )

    created = models.DateTimeField(
        auto_now=True,
        verbose_name='criado em'
    )

    def save(self, *args, **kwargs):
        self.human_display = self.get_human_display()
        super().save(*args, **kwargs)

    def get_human_display(self):
        if not self.question.accepts_options:
            return ''

        option = self.question.options.get(value=self.value)
        return option.name

    def get_value_display(self):
        """
        Resgata valor da resposta conforme a sua pergunta: se possui um
        display humanizado ou não.
        """

        return self.value

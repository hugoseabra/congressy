"""
    Answer domain model.
"""
from django.contrib.auth.models import User
from django.db import models

from survey.models import Question


class Answer(models.Model):
    """
        Answer domain model implementation.
    """

    class Meta:
        verbose_name = 'resposta'
        verbose_name_plural = 'respostas'

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='resposta',
        related_name='answers',
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='usuario',
        blank=True,
        null=True,
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
        self.human_display = self._get_human_display()
        super().save(*args, **kwargs)

    def _get_human_display(self):
        if not self.question.accepts_options:
            return None

        option = self.question.options.get(value=self.value)
        return option.name

    def get_value_display(self):
        """
        Resgata valor da resposta conforme a sua pergunta: se possui um
        display humanizado ou não.
        """
        if self.human_display is not None:
            return self.human_display

        return self.value

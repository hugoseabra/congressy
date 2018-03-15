"""
    Answer domain model.
    Resposta de um questionário, referente a uma pergunta a pertecente a um
    Autor.
"""
from django.db import IntegrityError, models

from survey.models import Author, Question


class Answer(models.Model):
    """
        Answer domain model implementation.
    """

    class Meta:
        verbose_name = 'resposta'
        verbose_name_plural = 'respostas'

    def __str__(self):
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
        self.human_display = self._get_human_display()
        super().save(*args, **kwargs)

    def _get_human_display(self):
        if not self.question.accepts_options:
            return None

        option = self.question.options.get(value=self.value)
        return option.name

    def clean(self):
        if self.question.survey != self.author.survey:
            raise IntegrityError(
                'A pergunta e o autor não pertencem ao mesmo '
                'questionário.'
            )

    def get_value_display(self):
        """
        Resgata valor da resposta conforme a sua pergunta: se possui um
        display humanizado ou não.
        """
        if self.human_display is not None:
            return self.human_display

        return self.value

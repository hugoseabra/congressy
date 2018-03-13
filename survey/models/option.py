"""
    Option domain model.
"""
from django.db import models
from . import Question


class Option(models.Model):
    """
        Option domain model implementation.
    """

    class Meta:
        verbose_name = 'Opção de uma pergunta'
        verbose_name_plural = 'Opções de uma pergunta'
        unique_together = (
            ('question', 'value',),
        )

    def __str__(self):
        return self.name + ' - ' + self.value

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='pergunta',
        related_name='options'
    )

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
    )

    value = models.CharField(
        max_length=255,
        verbose_name='valor',
    )

    active = models.BooleanField(
        default=True,
        verbose_name='ativo'
    )

    intro = models.BooleanField(
        default=False,
    )

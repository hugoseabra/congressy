"""
    Option domain model.
    Opção de uma pergunta que suporta múltiplas possibilidades de resposta.
"""
from django.db import models
from . import Question
from survey.models.mixins import Entity


class Option(Entity, models.Model):
    """
        Option domain model implementation.
    """

    class Meta:
        verbose_name = 'Opção de uma pergunta'
        verbose_name_plural = 'Opções de uma pergunta'
        unique_together = (
            ('question', 'value',),
        )

    def __str__(self):  # pragma: no cover
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
        null=True,
        blank=True,
    )

    active = models.BooleanField(
        default=True,
        verbose_name='ativo'
    )

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

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
        help_text='Nome da opção'
    )

    value = models.CharField(
        max_length=255,
        verbose_name='valor',
        help_text='Valor da opção'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='pergunta',
    )







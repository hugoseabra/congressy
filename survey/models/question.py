"""
    Question domain model.
"""
from django.db import models
from survey.models import Survey


class Question(models.Model):
    """
        Question domain model implementation.
    """

    class Meta:
        verbose_name = 'Pergunta de Questionario'
        verbose_name_plural = 'Perguntas de Questionario'

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='questionario',
    )

    type = models.CharField(
        max_length=50,
        verbose_name='tipo'
    )

    label = models.CharField(
        max_length=255,
        verbose_name='rotulo'
    )

    name = models.CharField(
        max_length=255,
        verbose_name='titulo',
    )

    required = models.BooleanField(
        default=False,
        verbose_name='obrigatoriedade',
    )

    help_text = models.CharField(
        max_length=255,
        verbose_name='texto de ajuda',
    )

    has_options = models.BooleanField(
        default=False,
        verbose_name='pergunta com opções',
    )

    active = models.BooleanField(
        default=True,
        verbose_name='ativo'
    )

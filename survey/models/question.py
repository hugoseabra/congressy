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

    name = models.CharField(
        max_length=255,
        verbose_name='titulo',
        help_text='Título da pergunta'
    )

    is_required = models.BooleanField(
        default=False,
        verbose_name='obrigatoriedade',
        help_text="Obrigatoriedade da pergunta"
    )

    is_complex = models.BooleanField(
        default=False,
        verbose_name='pergunta com opções',
        help_text="Pergunta possui opções."
    )

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='questionario',
    )


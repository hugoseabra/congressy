"""
    Survey domain model.
"""
from django.db import models
from . import Question


class Survey(models.Model):
    """
        Survey domain model implementation.
    """

    class Meta:
        verbose_name = 'Opção de uma pergunta'
        verbose_name_plural = 'Opções de uma pergunta'
        ordering = ['']



    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )







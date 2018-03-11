"""
    Answer domain model.
"""
from django.db import models
from survey.models import Question
from django.contrib.auth.models import User


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
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='usuario',
        blank=True,
        null=True,
    )

    value = models.TextField(
        verbose_name='valor'
    )

    human_display = models.CharField(
        max_length=255,
        verbose_name='nome exibido a humanos'
    )

    created = models.DateTimeField(
        auto_now=True,
        verbose_name='criado em'
    )

"""
    Author domain model.
    Autor de respostas de uma questionário.
"""
from django.contrib.auth.models import User
from django.db import models, IntegrityError

from survey.models import Survey


class Author(models.Model):
    """
        Author domain model implementation.
    """

    class Meta:
        verbose_name = 'autor'
        verbose_name_plural = 'autores'

    def __str__(self):
        return self.name

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='autor',
        related_name='authors',
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='usuario',
        blank=True,
        null=True,
        related_name='authors',
    )

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
    )

    created = models.DateTimeField(
        auto_now=True,
        verbose_name='criado em'
    )

    def clean(self):
        if isinstance(self.user, User) and self.user.is_anonymous:
            raise IntegrityError('Usuário não pode ser anônimo.')


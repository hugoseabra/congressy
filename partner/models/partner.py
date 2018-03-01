"""
    Model representation of the Partner entity in the Database
"""

from django.db import models
from gatheros_event.models import Person
from partner import constants


class Partner(models.Model):
    """
        Model implementation of the Partner entity
    """

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='partner',
    )

    status = models.CharField(
        choices=constants.STATUSES,
        default=constants.NON_ACTIVE,
        max_length=30,
        verbose_name="status",
    )

    approved = models.BooleanField(
        default=False,
        verbose_name="aprovado"
    )

    def __str__(self):
        return self.person.name

    class Meta:
        verbose_name = 'Parceiro'
        verbose_name_plural = 'Parceiros'


"""
    Model representation of the Partner entity in the Database
"""

from django.db import models

from gatheros_event.models import Person
from partner import constants
from payment.models import BankAccount


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

    bank_account = models.OneToOneField(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='partner',
        blank=True,
        null=True,
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

    recipient_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.person.name

    class Meta:
        verbose_name = 'Parceiro'
        verbose_name_plural = 'Parceiros'


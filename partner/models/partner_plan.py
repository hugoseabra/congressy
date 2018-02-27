"""
     Model representation of the Partner Plan entity in the Database
"""
from django.db import models


class PartnerPlan(models.Model):
    """
        Model implementation of the Partner Plan entity
    """
    name = models.CharField(
        max_length=255,
        verbose_name='nome'
    )

    percent = models.DecimalField(
        decimal_places=3,
        max_digits=11,
        verbose_name='porcentagem'
    )

    def __str__(self):
        return self.name



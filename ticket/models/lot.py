from decimal import Decimal

from django.db import models

from base.models import EntityMixin
from gatheros_event.models.mixins import GatherosModelMixin


class Lot(GatherosModelMixin, EntityMixin, models.Model):
    class Meta:
        verbose_name = "lote de ingressos"
        verbose_name_plural = "lotes de ingressos"
        unique_together = (
            ('ticket', 'date_start', 'date_end',),
        )

    ticket = models.ForeignKey(
        'ticket.Ticket',
        on_delete=models.CASCADE,
        verbose_name='ingresso de participante',
        related_name='lots',
        # Making field required
        blank=False,
        null=False,
    )

    date_start = models.DateTimeField(
        verbose_name='data/hora inicial',
        # Making field required
        blank=False,
        null=False,
    )

    date_end = models.DateTimeField(
        verbose_name='data/hora final',
        # Making field required
        blank=False,
        null=False,
    )

    price = models.DecimalField(
        verbose_name="preço",
        max_digits=8,
        decimal_places=2,
        default=Decimal(0.00),
        # Making field optional
        blank=True,
        null=True,
    )

    limit = models.PositiveIntegerField(
        verbose_name="limite de inscrições",
        # Making field optional
        blank=True,
        null=True,
        help_text="numero total de inscrições para que o lote"
    )

    num_subs = models.PositiveIntegerField(
        verbose_name="numero de inscrições",
        # Making field optional
        blank=True,
        default=0,
        null=True,
        editable=False,
        help_text="controle interno para contagem de inscrições",
    )

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='criado em'
    )

    modified = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name='modificado em'
    )

    def __str__(self):
        if self.name:
            return self.name

        return ''

    def __repr__(self):
        if self.name:
            return '{} - ID: {}'.format(
                self.name, str(self.pk)
            )

        return str(self.pk)

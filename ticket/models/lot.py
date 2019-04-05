from decimal import Decimal

from django.db import models


class Lot(models.Model):
    class Meta:
        verbose_name = "lote de inscriÃ§Ã£o"
        verbose_name_plural = "lotes de inscriÃ§Ã£o"
        unique_together = (
            ('audience_category', 'date_start', 'date_end',),
        )

    ticket = models.ForeignKey(
        'ticket.Ticket',
        on_delete=models.PROTECT,
        verbose_name='ingresso de participante',
        related_name='lots',
        # Making field required
        blank=False,
        null=False,
    )

    name = models.CharField(
        max_length=80,
        verbose_name="nome do lote",
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

    last = models.NullBooleanField(
        verbose_name="ultimo lote",
        # Making field optional
        blank=True,
        null=True,
        editable=False,
        help_text="controle inter para contagem de inscrições",
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
            return '{} - ID: {}'.format(
                self.name, str(self.pk)
            )

        return str(self.pk)

from django.db import models

from gatheros_event.models import Event
from gatheros_subscription.models import Subscription


class Raffle(models.Model):
    class Meta:
        verbose_name_plural = 'sorteios'
        verbose_name = 'sorteio'

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='raffles'
    )

    product_name = models.CharField(
        max_length=255,
        verbose_name='nome do produto'
    )

    quantity = models.PositiveSmallIntegerField(
        verbose_name='Quantidade',
        help_text='Quantos produtos serão sorteados?',
        default=1,
    )

    winner_out = models.BooleanField(
        verbose_name='retirar ganhadores',
        help_text='Ganhadores não serão sorteados novamente.'
    )

    attended_only = models.BooleanField(
        default=True,
        verbose_name='somente presentes',
        help_text='Somente presentes (check-in) participarão do sorteio.'
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em'
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name='modificado em'
    )


class Winner(models.Model):
    class Meta:
        verbose_name_plural = 'sorteios'
        verbose_name = 'sorteio'

    raffle = models.ForeignKey(
        Raffle,
        on_delete=models.CASCADE,
        verbose_name='sorteio',
        related_name='winners'
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='inscrição',
        related_name='raffle_winners'
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em'
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name='modificado em'
    )

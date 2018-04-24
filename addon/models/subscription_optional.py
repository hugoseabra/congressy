# pylint: disable=W5101

"""
    Representação dos opcionais(add ons) de inscrições(subscriptions)
"""

from django.db import models

from addon import rules
from base.models import EntityMixin
from gatheros_subscription.models import Subscription
from .optional import OptionalProduct, OptionalService


class AbstractSubscriptionOptional(EntityMixin, models.Model):
    """
        Vínculo de uma inscrição com um opcional, registrando,
        redundantemente, informações da Opcional informada para fins de
        auditoria.
    """
    rule_instances = (
        rules.MustBeSameOptionalLotCategory,
    )

    class Meta:
        abstract = True

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='%(class)s_optionals',
        verbose_name='inscrição',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="data de criação",
    )
    price = models.DecimalField(
        verbose_name='preço',
        decimal_places=2,
        max_digits=10,
    )

    count = models.PositiveIntegerField(
        verbose_name="quantidade até agora",
        default=0,
        blank=True,
    )
    total_allowed = models.PositiveIntegerField(
        verbose_name="total permitido",
    )


class SubscriptionOptionalProduct(AbstractSubscriptionOptional):
    """
        Vínculo de uma inscrição com um Opcional de Produto.
    """
    optional_product = models.ForeignKey(
        OptionalProduct,
        on_delete=models.CASCADE,
        verbose_name='opcional de produto',
        related_name='products'
    )


class SubscriptionOptionalService(AbstractSubscriptionOptional):
    """
        Vínculo de uma inscrição com um Opcional de Serviço.
    """
    optional_service = models.ForeignKey(
        OptionalService,
        on_delete=models.DO_NOTHING,
        verbose_name='opcional de serviço',
        related_name='services'
    )

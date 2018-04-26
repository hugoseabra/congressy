# pylint: disable=W5101

"""
    Representação dos opcionais(add ons) de inscrições(subscriptions)
"""

from django.db import models

from addon import rules
from base.models import EntityMixin
from gatheros_subscription.models import Subscription
from .optional import Product, Service


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
        related_name='%(class)s',
        verbose_name='inscrição',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="data de criação",
    )

    def __str__(self):
        return '{}: {}'.format(__name__, self.subscription.person.name)


class SubscriptionOptionalProduct(AbstractSubscriptionOptional):
    """
        Vínculo de uma inscrição com um Opcional de Produto.
    """
    optional = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='opcional de produto',
        related_name='products'
    )


class SubscriptionOptionalService(AbstractSubscriptionOptional):
    """
        Vínculo de uma inscrição com um Opcional de Serviço.
    """
    optional = models.ForeignKey(
        Service,
        on_delete=models.DO_NOTHING,
        verbose_name='opcional de serviço',
        related_name='services'
    )

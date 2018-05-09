# pylint: disable=W5101

"""
    Representação dos opcionais(add ons) de inscrições(subscriptions)
"""

from django.db import models

from addon import rules
from base.models import EntityMixin
from core.util.date import DateTimeRange
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
        ordering = ('subscription__event',)

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

    optional_price = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,
        blank=True,
    )

    optional_liquid_price = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,
        blank=True,
    )

    def __str__(self):
        return '{}: {}'.format(__name__, self.subscription.person.name)


class SubscriptionProduct(AbstractSubscriptionOptional):
    """
        Vínculo de uma inscrição com um Opcional de Produto.
    """

    class Meta(AbstractSubscriptionOptional.Meta):
        verbose_name_plural = 'inscrições de opcional de produto'
        verbose_name = 'inscrição de opcional de produto'

    optional = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='opcional de produto',
        related_name='subscription_products'
    )

    @property
    def num_consumed(self):
        """
        Resgata quantidade de opcionais vendidos/consumidos através de
        inscrições.

        :return: número de opcionais vendidos
        :type: bool
        """
        return self.optional.subscription_products.exclude(
            subscription__status='canceled'
        ).count()


class SubscriptionService(AbstractSubscriptionOptional):
    """
        Vínculo de uma inscrição com um Opcional de Serviço.
    """

    class Meta(AbstractSubscriptionOptional.Meta):
        verbose_name_plural = 'inscrições de opcional de serviço'
        verbose_name = 'inscrição de opcional de serviço'

    optional = models.ForeignKey(
        Service,
        on_delete=models.DO_NOTHING,
        verbose_name='opcional de serviço',
        related_name='subscription_services'
    )

    @property
    def num_consumed(self):
        """
        Resgata quantidade de opcionais vendidos/consumidos através de
        inscrições.

        :return: número de opcionais vendidos
        :type: bool
        """
        return self.optional.subscription_services.exclude(
            subscription__status='canceled'
        ).count()

    @property
    def has_schedule_conflicts(self):
        new_start = self.optional.schedule_start
        new_end = self.optional.schedule_end

        is_restricted = self.optional.restrict_unique

        for sub_optional in self.subscription.subscriptionservice.all():

            start = sub_optional.optional.schedule_start
            stop = sub_optional.optional.schedule_end
            is_sub_restricted = \
                sub_optional.optional.restrict_unique 

            session_range = DateTimeRange(start=start, stop=stop)
            has_conflict = (new_start in session_range or new_end in
                            session_range)

            if has_conflict is True and (is_restricted or is_sub_restricted):
                return True

        return False

    @property
    def get_schedule_conflict_service(self):
        new_start = self.optional.schedule_start
        new_end = self.optional.schedule_end

        is_restricted = self.optional.restrict_unique

        for sub_optional in self.subscription.subscriptionservice.all():

            start = sub_optional.schedule_start
            stop = sub_optional.schedule_end
            is_sub_restricted = \
                sub_optional.restrict_unique

            session_range = DateTimeRange(start=start, stop=stop)
            has_conflict = (new_start in session_range or new_end in
                            session_range)

            if has_conflict is True and (is_restricted or is_sub_restricted):
                return sub_optional

        return None

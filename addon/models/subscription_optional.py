# pylint: disable=W5101

"""
    Representação dos opcionais(add ons) de inscrições(subscriptions)
"""

from django.db import models

from addon import rules
from base.models import EntityMixin
from core.model import track_data
from core.util.date import DateTimeRange
from gatheros_subscription.models import Subscription
from .optional import Product, Service


@track_data('optional_price', 'optional_liquid_price')
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


@track_data('optional_id', 'subscription_id')
class SubscriptionProduct(AbstractSubscriptionOptional):
    """
        Vínculo de uma inscrição com um Opcional de Produto.
    """

    class Meta(AbstractSubscriptionOptional.Meta):
        verbose_name_plural = 'inscrições de opcional de produto'
        verbose_name = 'inscrição de opcional de produto'
        unique_together = ('subscription', 'optional',)

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='subscription_products',
        verbose_name='inscrição',
    )

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
            subscription__status=Subscription.CANCELED_STATUS,
            subscription__test_subscription=False,
            subscription__completed=True,
        ).count()

    def get_person_name(self):
        return self.subscription.person.name

    get_person_name.short_description = 'Participante'

    def get_optional_name(self):
        return self.optional.name

    get_optional_name.short_description = 'Produto'


@track_data('optional_id', 'subscription_id')
class SubscriptionService(AbstractSubscriptionOptional):
    """
        Vínculo de uma inscrição com um Opcional de Serviço.
    """

    class Meta(AbstractSubscriptionOptional.Meta):
        verbose_name_plural = 'inscrições de opcional de serviço'
        verbose_name = 'inscrição de opcional de serviço'
        unique_together = ('subscription', 'optional',)

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='subscription_services',
        verbose_name='inscrição',
    )

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
            subscription__status=Subscription.CANCELED_STATUS,
            subscription__test_subscription=False,
            subscription__completed=True,
        ).count()

    @property
    def has_schedule_conflicts(self):
        new_start = self.optional.schedule_start
        new_end = self.optional.schedule_end

        is_restricted = self.optional.restrict_unique

        for sub_optional in self.subscription.subscription_services.all():
            optional = sub_optional.optional

            start = optional.schedule_start
            stop = optional.schedule_end
            is_sub_restricted = optional.restrict_unique

            session_range = DateTimeRange(start=start, stop=stop)
            has_conflict = \
                (new_start in session_range or new_end in session_range)

            if has_conflict is True and (is_restricted or is_sub_restricted):
                return True

        return False

    @property
    def get_tag_conflict_services(self):
        sub_serv_qs = self.subscription.subscription_services

        existing_tag_qs = sub_serv_qs.filter(optional__tag=self.optional.tag)

        return existing_tag_qs.all() if existing_tag_qs.count() > 0 else list()

    @property
    def has_tag_conflict(self):
        tag_conflict_services = self.get_tag_conflict_services
        return len(tag_conflict_services) > 0

    @property
    def get_schedule_conflict_service(self):
        new_start = self.optional.schedule_start
        new_end = self.optional.schedule_end

        sub_serv_qs = self.subscription.subscription_services

        is_restricted = self.optional.restrict_unique

        for sub_optional in sub_serv_qs.all():
            optional = sub_optional.optional

            start = optional.schedule_start
            stop = optional.schedule_end
            is_sub_restricted = optional.restrict_unique

            dates_range = DateTimeRange(start=start, stop=stop)
            has_conflict = (new_start in dates_range or new_end in dates_range)

            if has_conflict is True and (is_restricted or is_sub_restricted):
                return sub_optional

        return None

    @property
    def has_conflict_services(self):
        has_tag_conflict = self.has_tag_conflict
        has_date_conflict = self.has_schedule_conflicts

        return has_tag_conflict is True or has_date_conflict is True

    def get_person_name(self):
        return self.subscription.person.name

    get_person_name.short_description = 'Participante'

    def get_optional_name(self):
        return self.optional.name

    get_optional_name.short_description = 'Serviço'

    def get_theme(self):
        return self.optional.theme.name

    get_theme.short_description = 'Áreas Temáticas'

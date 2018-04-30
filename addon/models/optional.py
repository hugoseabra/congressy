# pylint: disable=W5101

"""
    Representação do serviços de opcional(add ons)
"""
from decimal import Decimal

from django.db import models

from addon import constants, rules
from base.models import EntityMixin
from core.model import track_data
from gatheros_subscription.models import LotCategory
from .optional_type import OptionalServiceType, OptionalProductType
from .theme import Theme


@track_data('date_end_sub')
class AbstractOptional(EntityMixin, models.Model):
    """
        Opcional é um item adicional (add-on) à inscrição de um evento que
        será de um *produto* ou *serviço*.

        Opcionais permitem que possam adquirir produtos/serviços juntamente com
        a inscrição, separando a compra, pois a inscrição em sua venda própria
        e separada.
    """

    class Meta:
        abstract = True
        ordering = ('name',)

    lot_category = models.ForeignKey(
        LotCategory,
        on_delete=models.PROTECT,
        verbose_name='categoria',
        related_name='%(class)s_optionals'
    )

    name = models.CharField(
        max_length=255,
        verbose_name="nome",
    )

    date_end_sub = models.DateTimeField(
        verbose_name="Inscrição - data/hora limite",
        help_text='Data e hora limite para se aceitar inscrições para este'
                  ' opcional.'
    )

    published = models.BooleanField(
        verbose_name="publicado",
        default=True,
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado",
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name="modificado",
    )

    created_by = models.CharField(
        max_length=255,
        verbose_name="criado por",
    )

    modified_by = models.CharField(
        max_length=255,
        verbose_name="modificado por",
    )

    price = models.DecimalField(
        default=Decimal(0.00),
        verbose_name='preço',
        decimal_places=2,
        max_digits=10,
        blank=True,
    )

    description = models.TextField(
        verbose_name="descrição",
        null=True,
        blank=True,
    )

    quantity = models.PositiveIntegerField(
        verbose_name="quantidade",
        null=True,
        blank=True,
        help_text='Limite máximo permitido.'
    )

    release_days = models.PositiveIntegerField(
        verbose_name="dias de liberação de opcionais",
        default=constants.MINIMUM_RELEASE_DAYS,
        null=True,
        blank=True,
        help_text='Número de dias em que serão liberadas as vagas de opcionais'
                  ' caso a inscrição esteja como pendente.'
    )

    def __str__(self):
        return self.name


class Product(AbstractOptional):
    """
        Opcional de produto é um adicional de produto a ser comprado no ato da
        inscrição de um evento. Exemplo: camiseta, caneca, kit, dentre outros.
    """

    class Meta(AbstractOptional.Meta):
        verbose_name_plural = 'opcionais de produto'
        verbose_name = 'opcional de produto'

    rule_instances = (
        rules.OptionalMustHaveMinimumDays,
    )

    optional_type = models.ForeignKey(
        OptionalProductType,
        on_delete=models.PROTECT,
        verbose_name='tipo',
        related_name='product_type_optionals',
    )

    @property
    def num_consumed(self):
        """
        Resgata quantidade de opcionais vendidos/consumidos através de
        inscrições.

        :return: número de opcionais vendidos
        :type: bool
        """
        return self.subscription_products.count()


@track_data('schedule_start', 'schedule_end')
class Service(AbstractOptional):
    """
        Opcional de Serviço é um serviço a ser adquirido no ato da inscrição
        de um evento. Exemplo: curso, workshop, treinamento, dentre outros.
    """

    class Meta(AbstractOptional.Meta):
        verbose_name_plural = 'opcionais de serviço'
        verbose_name = 'opcional de serviço'

    rule_instances = (
        rules.MustScheduleDateEndAfterDateStart,
        rules.ServiceMustHaveUniqueDatetimeScheduleInterval,
        rules.OptionalMustHaveMinimumDays,
    )

    optional_type = models.ForeignKey(
        OptionalServiceType,
        on_delete=models.PROTECT,
        verbose_name='tipo',
        related_name='service_type_optionals',
    )

    theme = models.ForeignKey(
        Theme,
        on_delete=models.PROTECT,
        verbose_name="themas",
        related_name="services",
    )

    schedule_start = models.DateTimeField(
        verbose_name="programação - data/hora inicial",
        help_text='Data e hora inicial da programação no dia do evento.'
    )
    schedule_end = models.DateTimeField(
        verbose_name="programação - data/hora final",
        help_text='Data e hora final da programação no dia do evento.'
    )

    place = models.CharField(
        max_length=255,
        verbose_name='local',
        null=True,
        blank=True,
    )

    restrict_unique = models.BooleanField(
        default=False,
        verbose_name='restringir como único',
        help_text='Restringir como única dentro do intervalo de tempo.'
    )

    @property
    def num_consumed(self):
        """
        Resgata quantidade de opcionais vendidos/consumidos através de
        inscrições.

        :return: número de opcionais vendidos
        :type: bool
        """
        return self.subscription_services.count()

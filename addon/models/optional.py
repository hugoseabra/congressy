# pylint: disable=W5101

"""
    Representação do serviços de opcional(add ons)
"""

from django.db import models

from base.models import EntityMixin
from gatheros_subscription.models import LotCategory
from .optional_type import OptionalType
from .theme import Theme


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

    name = models.CharField(
        max_length=255,
        verbose_name="nome",
    )

    date_start = models.DateTimeField(verbose_name="data inicial",)
    date_end = models.DateTimeField(verbose_name="data final",)

    description = models.TextField(
        verbose_name="descrição",
    )

    quantity = models.PositiveIntegerField(
        verbose_name="quantidade",
        null=True,
        blank=True,
    )

    published = models.BooleanField(
        verbose_name="publicado",
        default=True,
    )

    has_cost = models.BooleanField(
        verbose_name="possui custo",
        default=False,
    )

    lot_categories = models.ManyToManyField(
        LotCategory,
        verbose_name='categorias',
        related_name='%(class)s_optionals'
    )

    optional_type = models.ForeignKey(
        OptionalType,
        on_delete=models.PROTECT,
        verbose_name='tipo',
        related_name='%(class)s_optionals',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado",
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name="modificado",
        null=True,
        editable=False,
    )

    created_by = models.CharField(
        null=True,
        editable=False,
        max_length=255,
        verbose_name="criado por",
    )

    modified_by = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="modificado por",
    )


class OptionalProduct(AbstractOptional):
    """
        Opcional de produto é um adicional de produto a ser comprado no ato da
        inscrição de um evento. Exemplo: camiseta, caneca, kit, dentre outros.
    """
    def __str__(self):
        return self.name


class OptionalService(AbstractOptional):
    """
        Opcional de Serviço é um serviço a ser adquirido no ato da inscrição
        de um evento. Exemplo: curso, workshop, treinamento, dentre outros.
    """
    start_on = models.DateTimeField(
        verbose_name="data de inicio",
    )

    duration = models.PositiveIntegerField(
        verbose_name="duração",
    )

    theme = models.ForeignKey(
        Theme,
        on_delete=models.PROTECT,
        verbose_name="themas",
        related_name="services",
    )

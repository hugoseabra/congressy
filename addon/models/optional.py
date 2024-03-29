# pylint: disable=W5101

"""
    Representação do serviços de opcional(add ons)
"""
import os
from datetime import datetime
from decimal import Decimal

from django.db import models
from stdimage import StdImageField
from stdimage.validators import MaxSizeValidator

from addon import constants, rules
from base.models import EntityMixin
from core.model import track_data
from core.util.date import DateTimeRange
from gatheros_event.models.mixins import GatherosModelMixin
from gatheros_subscription.models import LotCategory, Subscription
from .optional_type import OptionalServiceType, OptionalProductType
from .theme import Theme


def get_image_path(instance, filename):
    """ Resgata localização onde as imagens serão inseridas. """

    addon_type = str(instance.__class__.__name__).lower()

    return os.path.join(
        'event',
        str(instance.lot_category.event_id),
        'addon_{}'.format(addon_type),
        str(instance.id),
        os.path.basename(filename)
    )


@track_data('lot_category_id', 'date_end_sub', 'published', 'liquid_price',
            'description', 'quantity', 'release_days', 'banner', )
class AbstractOptional(GatherosModelMixin, EntityMixin, models.Model):
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

    OPTIONAL_STATUS_RUNNING = 'running'
    OPTIONAL_STATUS_FINISHED = 'finished'

    lot_category = models.ForeignKey(
        LotCategory,
        on_delete=models.PROTECT,
        verbose_name='categoria',
        related_name='%(class)s_optionals',
        help_text='Para qual categoria de participante se destina.',
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
        blank=True,
    )

    modified_by = models.CharField(
        max_length=255,
        verbose_name="modificado por",
        blank=True,
    )

    liquid_price = models.DecimalField(
        default=Decimal(0.00),
        verbose_name='preço líquido',
        decimal_places=2,
        max_digits=10,
        blank=True,
        help_text='Qual o valor liquido que você espera receber pela venda'
                  ' deste item opcional?'
    )

    description = models.CharField(
        max_length=150,
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

    banner = StdImageField(
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem',
        variations={'default': (900, 580), 'thumbnail': (135, 87, True)},
        validators=[MaxSizeValidator(2700, 1740)],
        help_text="Imagem de apresentação (tamanho"
                  " mínimo: 900px x 580px)."
    )

    def __str__(self):
        return self.name

    @property
    def status(self):
        """
        Status do opcional de acordo com suas datas.
        :return: string
        """
        if self.quantity and self.quantity > 0:
            if self.num_consumed >= self.quantity:
                return self.OPTIONAL_STATUS_FINISHED

        now = datetime.now()
        if now > self.date_end_sub:
            return self.OPTIONAL_STATUS_FINISHED

        return self.OPTIONAL_STATUS_RUNNING

    @property
    def running(self):
        return self.status == self.OPTIONAL_STATUS_RUNNING

    @property
    def finished(self):
        return self.status == self.OPTIONAL_STATUS_FINISHED

    @property
    def has_quantity_conflict(self):
        num_subs = self.num_consumed
        quantity = self.quantity or 0

        if 0 < quantity <= num_subs:
            return True

        return False

    @property
    def has_sub_end_date_conflict(self):
        if self.date_end_sub and datetime.now() > self.date_end_sub:
            return True

        return False

    @property
    def price(self):
        """
        Resgata o valor calculado do preço do lote de acordo com as regras
        da Congressy.
        """
        if self.liquid_price is None or self.liquid_price == 0:
            return Decimal(0)

        event = self.lot_category.event

        # minimum = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        congressy_plan_percent = Decimal(event.congressy_percent) / 100

        congressy_amount = self.liquid_price * congressy_plan_percent
        # if congressy_amount < minimum:
        #     congressy_amount = minimum

        return round(self.liquid_price + congressy_amount, 2)


@track_data('name', 'optional_type_id', 'tag')
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

    name = models.CharField(
        max_length=255,
        verbose_name="nome do produto",
    )

    optional_type = models.ForeignKey(
        OptionalProductType,
        on_delete=models.PROTECT,
        verbose_name='tipo',
        related_name='product_type_optionals',
        help_text='Exemplo: palestra, workshop, curso, hospedagem',
    )

    tag = models.CharField(
        max_length=24,
        verbose_name="Identificador único",
        help_text='Inscrições que são feitas em opcional que possui'
                  ' identificador único não podem fazer inscrição em outro'
                  ' opcional com o mesmo identificador.',
        null=True,
        blank=True,
    )

    @property
    def num_consumed(self):
        """
        Resgata quantidade de opcionais vendidos/consumidos através de
        inscrições.

        :return: número de opcionais vendidos
        :type: bool
        """
        return self.subscription_products.filter(
            subscription__completed=True,
            subscription__test_subscription=False
        ).exclude(subscription__status=Subscription.CANCELED_STATUS).count()

    def has_tag_conflict(self, subscription):
        if not self.tag:
            return False

        sub_subscribed = subscription.subscription_products.filter(
            optional_id=self.pk,
        ).count() > 0

        if sub_subscribed is True:
            # Inscrição já está inscrita no produto
            return False

        # Inscrições em produto
        return subscription.subscription_products.filter(
            optional__tag=self.tag,
        ).count() > 0

    def save(self, *args, **kwargs):
        if self.tag:
            self.tag = self.tag.upper()
            self.tag = self.tag.replace(' ', '')

        super().save(*args, **kwargs)


@track_data('name', 'optional_type_id', 'theme_id', 'schedule_start',
            'schedule_end', 'place', 'restrict_unique', 'tag')
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
        # rules.ServiceMustHaveUniqueDatetimeScheduleInterval,
        rules.ThemeMustBeSameEvent,
        rules.OptionalMustHaveMinimumDays,
    )

    name = models.CharField(
        max_length=255,
        verbose_name="nome da atividade",
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
        verbose_name="grupo temático",
        related_name="services",
        help_text='Agrupar atividades por área temática.',
    )

    schedule_start = models.DateTimeField(
        verbose_name="programação - início",
        help_text='Data e hora inicial da programação no dia do evento.'
    )

    schedule_end = models.DateTimeField(
        verbose_name="programação - fim",
        help_text='Data e hora final da programação no dia do evento.'
    )

    place = models.CharField(
        max_length=255,
        verbose_name='local',
        null=True,
        blank=True,
        help_text='Local onde a atividade irá acontecer no dia do evento.',
    )

    restrict_unique = models.BooleanField(
        default=False,
        verbose_name='Restringir horário',
        help_text='Se marcado, os participantes inscritos nesta atividade'
                  ' não poderão se inscrever em outras atividades que estejam'
                  ' em conflito de horário com esta.'
    )

    tag = models.CharField(
        max_length=24,
        verbose_name="Identificador único",
        help_text='Inscrições que são feitas em atividade extra que possui'
                  ' identificador único não podem fazer inscrição em outra'
                  ' atividadade extra com o mesmo identificador.',
        null=True,
        blank=True,
    )

    @property
    def num_consumed(self):
        """
        Resgata quantidade de opcionais vendidos/consumidos através de
        inscrições.

        :return: número de opcionais vendidos
        :type: bool
        """
        return self.subscription_services.filter(
            subscription__completed=True,
            subscription__test_subscription=False,
        ).exclude(subscription__status=Subscription.CANCELED_STATUS).count()

    @property
    def theme_full(self):
        return self.theme.limit and self.theme.limit >= self.num_consumed

    def save(self, *args, **kwargs):
        if self.tag:
            self.tag = self.tag.upper()
            self.tag = self.tag.replace(' ', '')

        super().save(*args, **kwargs)

    def get_period(self):
        """Recupera string de período de evento de acordo com as datas."""
        start_date = self.schedule_start.date()
        end_date = self.schedule_end.date()
        start_time = self.schedule_start.time()
        end_time = self.schedule_end.time()

        period = ''
        if start_date < end_date:
            period = 'De ' + self.schedule_start.strftime('%d/%m/%Y %Hh%M')
            period += ' a ' + self.schedule_end.strftime('%d/%m/%Y %Hh%M')

        if start_date == end_date:
            period = self.schedule_start.strftime('%d/%m/%Y')
            period += ' das '
            period += start_time.strftime('%Hh%M')
            period += ' às '
            period += end_time.strftime('%Hh%M')

        return period

    def has_schedule_conflict(self, subscription):
        sub_subscribed = subscription.subscription_services.filter(
            optional_id=self.pk,
        ).count() > 0

        if sub_subscribed is True:
            # Inscrição já está inscrita no serviço
            return False

        # Inscrições em serviços
        sub_services = subscription.subscription_services.all()

        new_start = self.schedule_start
        new_end = self.schedule_end

        # Este serviço restringe outros serviços
        is_restricted = self.restrict_unique

        for sub_optional in sub_services:
            optional = sub_optional.optional

            start = optional.schedule_start
            end = optional.schedule_end

            # serviço também restrito a outros servios
            is_sub_restricted = optional.restrict_unique

            dates_range = DateTimeRange(start=start, stop=end)
            has_conflict = (new_start in dates_range or new_end in dates_range)

            if has_conflict is True and (is_restricted or is_sub_restricted):
                return True

        return False

    def has_tag_conflict(self, subscription):
        if not self.tag:
            return False

        sub_subscribed = subscription.subscription_services.filter(
            optional_id=self.pk,
        ).count() > 0

        if sub_subscribed is True:
            # Inscrição já está inscrita no serviço
            return False

        # Inscrições em serviços
        return subscription.subscription_services.filter(
            optional__tag=self.tag,
        ).count() > 0

    def has_theme_conflict(self, subscription):
        if not self.theme.limit:
            return False

        sub_subscribed = subscription.subscription_services.filter(
            optional_id=self.pk,
        ).count() > 0

        if sub_subscribed is True:
            # Inscrição já está inscrita no serviço
            return False

        # Número de Inscrições em serviços com o mesmo tema
        num_sub_services = subscription.subscription_services.filter(
            optional__theme_id=self.theme.pk,
        ).count()

        return num_sub_services >= self.theme.limit

    def __str__(self):
        return '{} - {}'.format(self.name, self.theme.name)

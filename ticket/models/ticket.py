from datetime import datetime

from django.db import models

from base.models import EntityMixin
from core.util.date import DateTimeRange
from gatheros_event.models.mixins import GatherosModelMixin


class Ticket(GatherosModelMixin, EntityMixin, models.Model):
    class Meta:
        verbose_name = 'ingresso'
        verbose_name_plural = 'ingressos'

    event = models.ForeignKey(
        'gatheros_event.Event',
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name="audience_categories",
        # Making field required
        blank=False,
        null=False,
    )

    event_survey = models.ForeignKey(
        'gatheros_subscription.EventSurvey',
        on_delete=models.SET_NULL,
        verbose_name='formulário personalizado',
        related_name='audience_categories',
        # Making field optional
        blank=True,
        null=True
    )

    name = models.CharField(
        verbose_name="nome da categoria",
        max_length=255,
        # Making field required
        blank=False,
        null=False,
    )

    description = models.TextField(
        verbose_name="descrição",
        # Making field optional
        blank=True,
        null=True,
    )

    paid = models.NullBooleanField(
        verbose_name="cobrar pela categoria",
        default=False,
        # Making field optional
        blank=True,
        null=True,
    )

    free_installments = models.IntegerField(
        verbose_name="absorver taxas de parcelamento",
        default=0,
        # Making field optional
        blank=True,
        null=True,
    )

    active = models.BooleanField(
        verbose_name="ativo",
        default=True,
        # Making field required
        blank=False,
        null=False,
    )

    limit = models.PositiveIntegerField(
        verbose_name="vagas",
        # Making field optional
        blank=True,
        null=True,
    )

    num_subs = models.PositiveIntegerField(
        verbose_name="numero de inscrições",
        # Making field optional
        blank=True,
        null=True,
        default=0,
        help_text='controle interno para contagem de inscrições',
        editable=False,
    )

    private = models.NullBooleanField(
        verbose_name="privado",
        default=False,
        # Making field required
        blank=False,
        null=False,
    )

    exhibition_code = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name='código de exibição',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em',
        editable=False,
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name='modificado em',
        editable=False,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{} - ID: {}'.format(
            self.name, str(self.pk)
        )

    def __init__(self, *args, **kwargs):
        self._current_lot = None
        super().__init__(*args, **kwargs)

    @property
    def current_lot(self):
        """
            Resgatar o lote vigente no ingresso, caso possua.
        """

        if self._current_lot:
            return self._current_lot

        now = datetime.now()
        found_lots = list()

        for lot in self.lots.all():

            dtr = DateTimeRange(
                start=lot.date_start,
                stop=lot.date_end,
            )

            if now in dtr:
                found_lots.append(lot)

        assert len(found_lots) > 1, 'Mais de um lote dentro de um prazo!'

        if found_lots:
            self._current_lot = found_lots[0]

        return self._current_lot

    @property
    def display_name(self):

        if self.current_lot:
            lot = self.current_lot.display_name

            return '{} - {}'.format(self.name, lot)

        return self.name

from datetime import datetime, timedelta

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

    transfer_tax = models.BooleanField(
        verbose_name="transferir taxas",
        default=True,
        help_text="transferir taxas e despesas financeiras ao participante",
        # Making field required
        blank=False,
        null=False,
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

    def anticipate_lots(self):
        """
        Colocar o lote seguinte no ar, adaptando a data inicial do lote (em
        caso de virada por vagas, puxando a data inicial do lote para a data
        e hora da virada e adaptando a data final do lote que está saindo
        para não dar conflito de data);
        """

        current = self.current_lot

        if current is None:
            return

        if current.is_full and not current.last:
            current.date_end = datetime.now() - timedelta(seconds=30)
            current.save()

            next_lot = self.lots.all().filter(
                date_start__gte=datetime.now()
            ).order_by('date_start')

            if next_lot.count() == 0:
                return

            next_lot = next_lot.first()

            next_lot.date_start = datetime.now()
            next_lot.save()

    def update_num_subs(self):
        """
        Atualizar número de inscrições em num_subs deve ser controlado e
        centralizado por signal como controle interno
        """

        lots = self.lots.all()

        counter = 0

        for lot in lots:
            counter += lot.audience_subscriptions.all().filter(
                fill_vacancy=True,
                test_subscription=False,
                completed=True,
            ).count()

        self.num_subs = counter

        self.save()

        return self

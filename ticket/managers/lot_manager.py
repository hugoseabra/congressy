from django.core.exceptions import ValidationError
from django.db.models import Sum

from base.managers import Manager
from core.util.date import DateTimeRange
from gatheros_subscription.models import Subscription
from ticket.models import Lot


class LotManager(Manager):
    class Meta:
        model = Lot
        fields = '__all__'

    def clean_price(self):
        price = self.cleaned_data.get('price')

        # Ignore on creation
        if self.instance.pk is None:
            return price

        if price and self._lot_has_subscriptions():
            raise ValidationError(
                "não é possivel alterar o preço quando há inscrições"
            )

        return price

    def clean_limit(self):

        limit = self.cleaned_data.get('limit')
        ticket = self.cleaned_data.get('ticket')

        if limit is None:
            limit = 0

        ticket_limit = ticket.limit or 0

        limit_count = Lot.objects.filter(ticket_id=ticket.pk) \
            .aggregate(all_limit=Sum('limit'))

        if not limit_count['all_limit']:
            limit_count = 0 + limit
        else:
            limit_count = limit_count['all_limit'] + limit

        if limit_count > ticket_limit:
            raise ValidationError(
                "a soma dos limites dos lotes ultrapassam o numero de "
                "vagas da categoria"
            )

    def clean(self):
        cleaned_data = super().clean()

        self._clean_dates()

        return cleaned_data

    def _lot_has_subscriptions(self):

        return bool(
            Subscription.objects.filter(
                ticket_lot_id=self.instance.pk,
                test_subscription=False,
                completed=True,
                status=Subscription.CONFIRMED_STATUS,
            ).count()
        )

    def _clean_dates(self):

        date_start = self.cleaned_data.get('date_start')
        date_end = self.cleaned_data.get('date_end')
        ticket = self.cleaned_data.get('ticket')

        if date_start == date_end:
            raise ValidationError("Data de inicio e fim não podem ser iguais")

        if date_end < date_start:
            raise ValidationError("Data de fim não podem ser maior que data "
                                  "de inicio")

        existing_lots = ticket.lots.all()

        if self.instance.pk is not None:
            existing_lots = existing_lots.exclude(pk=self.instance.pk)

        for lot in existing_lots:
            start = lot.date_start.strftime('%d/%m/%Y %H:%M:%S')
            dtr = DateTimeRange(start=lot.date_start, stop=lot.date_end)

            if date_start.strftime('%d/%m/%Y %H:%M:%S') == start:
                msg = "Esse lote possui a mesma data de inicio com o lote " \
                      "'{}'".format(lot.name)
                raise ValidationError(msg)

            if date_start in dtr:
                msg = "Esse lote possui a data de inicio dentro do " \
                      "lote: '{}'".format(lot.name)
                raise ValidationError(msg)

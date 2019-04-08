from django.core.exceptions import ValidationError
from django.db.models import Sum

from base.managers import Manager
from core.util.date import DateTimeRange
from gatheros_subscription.models import Subscription
from ticket.models import Lot


class TicketManager(Manager):
    class Meta:
        model = Lot
        fields = '__all__'

    def clean_free_installments(self):
        free_installments = self.cleaned_data['free_installments']
        if free_installments and free_installments > 10:
            raise ValidationError('é possivel absorver no máximo 10 parcelas')

        return free_installments


class LotManager(Manager):
    class Meta:
        model = Lot
        fields = '__all__'

    def clean_price(self):
        price = self.cleaned_data['price']

        if price and self._lot_has_subscriptions():
            raise ValidationError(
                "não é possivel alterar o preço quando há inscrições nesse lote"
            )

        return price

    def clean_limit(self):

        limit = self.cleaned_data['limit']
        ticket = self.cleaned_data['ticket']

        ticket_limit = ticket.limit

        if limit and ticket_limit:

            limit_count = Lot.objects.filter(ticket_id=ticket.pk) \
                .aggregate(all_limit=Sum('limit'))

            if not limit_count['all_limit']:
                limit_count = 0
            else:
                limit_count = limit_count['all_limit'] + limit

            if limit_count > ticket_limit:
                raise ValidationError(
                    "a soma dos limites dos lotes ultrapassam o numero de "
                    "vagas da categoria")

    def clean(self):
        cleaned_data = super().clean()

        self._clean_dates()

        return cleaned_data

    def _lot_has_subscriptions(self):

        return bool(
            Subscription.objects.filter(
                ticket_id=self.instance.pk,
                test_subscription=False,
                completed=True,
                fill_vacancy=True,
                status=Subscription.CONFIRMED_STATUS,
            ).count()
        )

    def _clean_dates(self):

        ticket = self.cleaned_data['audience_category']

        existing_lots = Lot.objects.filter(
            tick_id=ticket.pk,
        )

        if hasattr(self.instance, 'pk'):
            existing_lots = existing_lots.exclude(pk=self.instance.pk)

        new_start = self.cleaned_data['date_start']

        for lot in existing_lots:
            start = lot.date_start
            end = lot.date_end
            session_range_two = DateTimeRange(start=start, stop=end)

            if new_start == start:
                msg = "Esse lote possui a mesma data de inicio com o lote " \
                      "'{}'".format(lot.name)
                raise ValidationError(msg)

            if new_start in session_range_two:
                msg = "Esse lote possui a mesma data de inicio dentro do " \
                      "lote: '{}'".format(lot.name)
                raise ValidationError(msg)

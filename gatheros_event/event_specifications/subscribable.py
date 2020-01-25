from datetime import datetime

from gatheros_event.models import Event
from gatheros_subscription.models import Lot, Subscription
from .mixins import EventCompositeSpecificationMixin, \
    LotCompositeSpecificationMixin


class EventSubscribable(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento possui algum lote quer permita
        que ele seja capaz de receber inscrições no presente ou futuro
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        if event.date_end < datetime.now():
            return False

        subscribable_lot_flag = False
        for lot in event.lots.all():
            lot_spec = LotSubscribable()
            if lot_spec.is_satisfied_by(lot):
                subscribable_lot_flag = True
                break

        if subscribable_lot_flag is False:
            return False

        valid_subs = Subscription.objects.filter(
            event=event,
            test_subscription=False,
            status=Subscription.CONFIRMED_STATUS,
        ).count()

        expected_subs = event.expected_subscriptions
        if expected_subs and expected_subs <= valid_subs:
            return False

        return True


class LotSubscribable(LotCompositeSpecificationMixin):
    """
        Essa especificação informa se o lote possui seja capaz de receber
        inscrições no presente ou futuro
    """

    def is_satisfied_by(self, lot: Lot):
        super().is_satisfied_by(lot)
        return lot.active is True and lot.running is True

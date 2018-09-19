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

        if event.date_end < datetime.now() or event.date_start < datetime.now():
            return False

        lots = event.lots.all()

        if lots.count() == 0:
            return False

        subscribable_lot_flag = False
        for lot in lots:
            lot_spec = LotSubscribable()
            if lot_spec.is_satisfied_by(lot):
                subscribable_lot_flag = True

        if not subscribable_lot_flag:
            return False

        valid_subs = Subscription.objects.filter(
            event=event,
            test_subscription=False,
            status=Subscription.CONFIRMED_STATUS,
        ).count()

        if event.expected_subscriptions and \
                valid_subs > event.expected_subscriptions:
            return False

        return True


class LotSubscribable(LotCompositeSpecificationMixin):
    """
        Essa especificação informa se o lote possui seja capaz de receber
        inscrições no presente ou futuro
    """

    def is_satisfied_by(self, lot: Lot):
        super().is_satisfied_by(lot)

        if not lot.active:
            return False

        now = datetime.now()
        if now > lot.date_end:
            return False

        return True

from core.specification import AndSpecification
from gatheros_event.event_specifications import (
    LotVisible,
    LotSubscribable,
    LotHasSubscriptions,
    EventVisible,
    EventPayable,
    ClosedWithNoAudience,
    ClosedWithAudience,
    OpenWithNoAudience,
    OpenWithAudience,
)

from gatheros_event.models import Event


class EventState(object):
    """
        Objetivo: Obter um evento e receber informações sobre o estado do mesmo.
    """

    def __init__(self, event: Event) -> None:
        self.event = event

    def is_public(self) -> bool:

        if ClosedWithNoAudience().is_satisfied_by(self.event):
            for lot in self.event.lots.all():
                if LotVisible().is_satisfied_by(lot):
                    return True

        elif ClosedWithAudience().is_satisfied_by(self.event):
            for lot in self.event.lots.all():

                one = LotVisible()
                other = LotHasSubscriptions()

                spec = AndSpecification(one, other)
                if spec.is_satisfied_by(lot):
                    return True

        elif OpenWithNoAudience().is_satisfied_by(self.event):
            for lot in self.event.lots.all():

                one = LotVisible()
                other = LotVisible()

                spec = AndSpecification(one, other)
                if spec.is_satisfied_by(lot):
                    return True

        elif OpenWithAudience().is_satisfied_by(self.event):
            for lot in self.event.lots.all():

                one = LotVisible()
                other = LotVisible()

                spec = AndSpecification(one, other)
                if spec.is_satisfied_by(lot):
                    return True

        return False

    def is_private(self) -> bool:

        if ClosedWithNoAudience().is_satisfied_by(self.event):

            if EventVisible().not_specification().is_satisfied_by(self.event):
                return True

        elif ClosedWithAudience().is_satisfied_by(self.event):

            if EventVisible().not_specification().is_satisfied_by(self.event):
                return True

            public_lot_with_no_subs = False
            private_lot_with_subs = False

            for lot in self.event.lots.all():

                one = LotVisible()
                other = LotHasSubscriptions().not_specification()

                public_lot_spec = AndSpecification(one, other)
                if public_lot_spec.is_satisfied_by(lot):
                    public_lot_with_no_subs = True

                one = LotVisible().not_specification()
                other = LotHasSubscriptions()

                private_lot_spec = AndSpecification(one, other)
                if private_lot_spec.is_satisfied_by(lot):
                    private_lot_with_subs = True

            if public_lot_with_no_subs and private_lot_with_subs:
                return True

        elif OpenWithNoAudience().is_satisfied_by(self.event):
            if EventVisible().not_specification().is_satisfied_by(self.event):
                return True

            for lot in self.event.lots.all():

                one = LotVisible().not_specification()
                other = LotSubscribable()

                spec = AndSpecification(one, other)
                if spec.is_satisfied_by(lot):
                    return True

        elif OpenWithAudience().is_satisfied_by(self.event):
            if EventVisible().not_specification().is_satisfied_by(self.event):
                return True

        return False

    def is_payable(self) -> bool:

        if EventPayable().is_satisfied_by(self.event):
            return True

        return False

    def is_free(self) -> bool:

        spec = EventPayable().not_specification()

        if spec.is_satisfied_by(self.event):
            return True

        return False

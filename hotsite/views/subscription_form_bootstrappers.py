from base.form_step import StepBootstrapper
from gatheros_event.models import Person
from gatheros_subscription.models import Lot, Subscription


class LotBootstrapper(StepBootstrapper):
    fallback_step = 'step_1'
    artifact_type = Lot

    def __init__(self, **kwargs) -> None:

        self.event = kwargs.get('event')
        self.lot_pk = kwargs.get('lot_pk', None)
        super().__init__()

    def retrieve_artifact(self):

        lot = None

        if self.lot_pk:
            try:
                lot = Lot.objects.get(pk=int(self.lot_pk), event=self.event)
            except Lot.DoesNotExist:
                pass

        return lot


class PersonBootstrapper(StepBootstrapper):
    fallback_step = 'step_2'
    artifact_type = Lot

    def __init__(self, **kwargs) -> None:
        self.person_pk = kwargs.get('person_pk', None)
        super().__init__()

    def retrieve_artifact(self):

        person = None

        if self.person_pk:
            try:
                person = Person.objects.get(pk=self.person_pk)
            except Person.DoesNotExist:
                pass

        return person


class SubscriptionBootstrapper(StepBootstrapper):
    fallback_step = 'step_2'
    artifact_type = Subscription

    def __init__(self, **kwargs) -> None:
        self.subscription_pk = kwargs.get('subscription_pk', None)
        super().__init__()

    def retrieve_artifact(self):

        subscription = None

        if self.subscription_pk:
            try:
                subscription = Subscription.objects.get(
                    pk=self.subscription_pk)
            except Subscription.DoesNotExist:
                pass

        return subscription

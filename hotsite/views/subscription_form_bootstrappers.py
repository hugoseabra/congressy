from base.step import StepBootstrapper
from gatheros_event.models import Person
from gatheros_subscription.models import Lot, Subscription, EventSurvey


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


class EventSurveyBootstrapper(StepBootstrapper):
    fallback_step = 'step_2'
    artifact_type = EventSurvey

    def __init__(self, **kwargs) -> None:
        self.event_survey_pk = kwargs.get('event_survey_pk', None)
        super().__init__()

    def retrieve_artifact(self):

        event_survey = None

        if self.event_survey_pk:
            try:
                event_survey = EventSurvey.objects.get(
                    pk=self.event_survey_pk)
            except EventSurvey.DoesNotExist:
                pass

        return event_survey


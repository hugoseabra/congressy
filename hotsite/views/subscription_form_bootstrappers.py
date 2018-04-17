from base.step import StepBootstrapper
from gatheros_event.models import Person
from gatheros_subscription.models import Lot, Subscription, EventSurvey


class LotBootstrapper(StepBootstrapper):

    @staticmethod
    def retrieve_artifact(antecessor_form=None, dirty_antecessor_data=None,
                          **kwargs):

        if antecessor_form:
            lot = antecessor_form.cleaned_data.get('lots')
        elif dirty_antecessor_data:
            lot = dirty_antecessor_data.get('lot')
        else:
            lot = None

        event = kwargs.get('event')

        if not event:
            raise Exception('Event not in kwargs')

        if lot and not isinstance(lot, Lot):
            try:
                lot = Lot.objects.get(pk=lot, event=event)
            except Person.DoesNotExist:
                pass

        return lot


class LotCouponCodeBootstrapper(StepBootstrapper):

    @staticmethod
    def retrieve_artifact(antecessor_form=None, dirty_antecessor_data=None,
                          **kwargs):

        if dirty_antecessor_data:
            coupon_code = dirty_antecessor_data.get('coupon_code')
        else:
            coupon_code = None

        return coupon_code


class PersonBootstrapper(StepBootstrapper):
    artifact_type = Person

    def retrieve_artifact(self, antecessor_form):

        person = antecessor_form.get('person')

        if person and not isinstance(person, self.artifact_type):
            try:
                person = Person.objects.get(pk=person)
            except Person.DoesNotExist:
                pass

        return person


class SubscriptionBootstrapper(StepBootstrapper):
    artifact_type = Subscription

    def retrieve_artifact(self, antecessor_form):

        subscription = antecessor_form.get('subscription')

        if subscription and not isinstance(subscription, self.artifact_type):
            try:
                subscription = Subscription.objects.get(pk=subscription)
            except Subscription.DoesNotExist:
                pass

        return subscription
# 
# 
# class EventSurveyBootstrapper(StepBootstrapper):
#     fallback_step = 'step_2'
#     artifact_type = EventSurvey
# 
#     def __init__(self, **kwargs) -> None:
#         self.event_survey_pk = kwargs.get('event_survey_pk', None)
#         super().__init__()
# 
#     def retrieve_artifact(self):
# 
#         event_survey = None
# 
#         if self.event_survey_pk:
#             try:
#                 event_survey = EventSurvey.objects.get(
#                     pk=self.event_survey_pk)
#             except EventSurvey.DoesNotExist:
#                 pass
# 
#         return event_survey

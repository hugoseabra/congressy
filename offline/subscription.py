from .base import Base, FilterMixin


class SubscriptionOffline(Base, FilterMixin):
    filter_dict = {
        'gatheros_subscription.EventSurvey': 'event_id',
    }

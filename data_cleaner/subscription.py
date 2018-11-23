from .base import DataCleanerBase, FilterMixin


class SubscriptionDataCleaner(DataCleanerBase, FilterMixin):
    filter_dict = (
        ('gatheros_subscription.Subscription', 'event_id'),
        ('gatheros_subscription.EventSurvey', 'event_id'),
        ('gatheros_subscription.Lot', 'event_id'),
        ('gatheros_subscription.LotCategory', 'event_id'),
        ('gatheros_subscription.FormConfig', 'event_id',),
     )

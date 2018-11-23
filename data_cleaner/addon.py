from .base import DataCleanerBase, FilterMixin


class AddonDataCleaner(DataCleanerBase, FilterMixin):
    filter_dict = (
        ('addon.SubscriptionProduct', 'optional__lot_category__event_id',),
        ('addon.SubscriptionService', 'optional__lot_category__event_id',),
        ('addon.Product', 'lot_category__event_id',),
        ('addon.Service', 'lot_category__event_id',),
        ('addon.Theme', 'event_id',),
    )

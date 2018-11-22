from .base import OfflineBase, FilterMixin


class AddonOffline(OfflineBase, FilterMixin):
    filter_dict = (
        ('addon.SubscriptionProduct', 'optional__lot_category__event_id',),
        ('addon.SubscriptionService', 'optional__lot_category__event_id',),
        ('addon.Product', 'lot_category__event_id',),
        ('addon.Service', 'lot_category__event_id',),
        ('addon.Theme', 'event_id',),
    )

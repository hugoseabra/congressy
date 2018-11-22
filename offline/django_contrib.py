from .base import OfflineBase, FilterMixin


class DjangoContribOffline(OfflineBase, FilterMixin):
    filter_dict = (
        ('auth.User', 'person__subscriptions__event_id',),
    )

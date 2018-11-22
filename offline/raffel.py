from .base import OfflineBase, FilterMixin


class RaffleOffline(OfflineBase, FilterMixin):
    filter_dict = (
        ('raffle.Raffle', 'event_id'),
        ('raffle.Winner', 'raffle__event_id'),
    )

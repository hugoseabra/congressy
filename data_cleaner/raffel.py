from .base import DataCleanerBase, FilterMixin


class RaffleDataCleaner(DataCleanerBase, FilterMixin):
    filter_dict = (
        ('raffle.Raffle', 'event_id'),
        ('raffle.Winner', 'raffle__event_id'),
    )

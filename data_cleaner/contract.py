from .base import DataCleanerBase, FilterMixin


class ContractDataCleaner(DataCleanerBase, FilterMixin):
    filter_dict = (
        ('installment.Contract', 'subscription__event_id',),
    )

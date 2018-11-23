from .base import DataCleanerBase, EraserMixin


class PartnerDataCleaner(DataCleanerBase, EraserMixin):
    erase_list = [
        'partner.Partner',
        'partner.PartnerPlan',
        'partner.PartnerContract',
    ]

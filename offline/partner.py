from .base import OfflineBase, EraserMixin


class PartnerOffline(OfflineBase, EraserMixin):
    erase_list = [
        'partner.Partner',
        'partner.PartnerPlan',
        'partner.PartnerContract',
    ]

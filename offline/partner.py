from .base import Base, EraserMixin


class PartnerOffline(Base, EraserMixin):
    erase_list = [
        'partner.Partner',
        'partner.PartnerPlan',
        'partner.PartnerContract',
    ]

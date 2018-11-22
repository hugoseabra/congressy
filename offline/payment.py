from .base import Base, EraserMixin


class PaymentOffline(Base, EraserMixin):
    erase_list = [
        'payment.BankAccount',
    ]

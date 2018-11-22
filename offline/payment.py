from .base import OfflineBase, EraserMixin, FilterMixin


class PaymentOffline(OfflineBase, EraserMixin, FilterMixin):
    erase_list = [
        'payment.BankAccount',
    ]

    filter_dict = (
        ('payment.Transaction', 'subscription__event_id'),
        ('payment.TransactionStatus', 'transaction__subscription__event_id'),
        ('payment.Payment', 'transaction__subscription__event_id'),
        ('payment_debt.Debt', 'subscription__event_id'),
        ('payment_debt.DebtConfig', 'debt__subscription__event_id'),
    )

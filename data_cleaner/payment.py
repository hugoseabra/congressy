from .base import DataCleanerBase, EraserMixin, FilterMixin


class PaymentDataCleaner(DataCleanerBase, EraserMixin, FilterMixin):
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

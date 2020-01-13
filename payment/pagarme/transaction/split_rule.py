from decimal import Decimal

from payment.helpers.payment_helpers import as_payment_amount


class SplitRule:
    def __init__(self,
                 recipient_id: str,
                 amount: Decimal,
                 liable: bool,
                 charge_processing_fee: bool):

        self.recipient_id = recipient_id
        self.amount = amount
        self.liable = liable
        self.charge_processing_fee = charge_processing_fee

        self.errors = dict()
        self._check_errors()

    def is_valid(self):
        self._check_errors()
        return len(self.errors) == 0

    def _check_errors(self):
        self.errors = dict()

        if not self.amount:
            self.errors['amount'] = 'Você deve informar um valor.'

    def __iter__(self):

        if self.is_valid() is False:
            msg = 'SplitRule não está válido:'

            for k, v in self.errors.items():
                msg += ' {}: {}.'.format(k, v)

            raise Exception(msg)

        iters = {
            'recipient_id': self.recipient_id,
            'amount': as_payment_amount(self.amount),
            'liable': self.liable is True,
            'charge_processing_fee': self.charge_processing_fee is True,
        }

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y

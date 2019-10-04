from decimal import Decimal

from payment.helpers.payment_helpers import as_payment_format


class Item:
    def __init__(self,
                 identifier: str,
                 title: str,
                 unit_price: Decimal,
                 liquid_unit_price: Decimal,
                 quantity: int,
                 tangible: bool):

        self.identifier = identifier
        self.title = title
        self.unit_price = unit_price
        self.liquid_unit_price = liquid_unit_price
        self.quantity = quantity
        self.tangible = tangible

        self.errors = dict()
        self._check_errors()

    def is_valid(self):
        return len(self.errors) == 0

    def _check_errors(self):
        if not self.unit_price:
            self.errors['unit_price'] = 'Você deve informar um valor.'

    def __iter__(self):

        if self.is_valid() is False:
            msg = 'Item não está válido:'

            for k, v in self.errors.items():
                msg += ' {}: {}.'.format(k, v)

            raise Exception(msg)

        iters = {
            'id': self.identifier,
            'title': self.title,
            'unit_price': as_payment_format(self.unit_price),
            'quantity': self.quantity,
            'tangible': self.tangible is True,
        }

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y

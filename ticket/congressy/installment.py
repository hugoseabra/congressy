from decimal import Decimal

from django.conf import settings


class CongressyInstallment:
    """
    Cálculo de transação a ser feita pelo Pagarme sempre levando em
    conta 2 recebedores.
    """
    interests_rate = \
        Decimal(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE) / 100

    def __init__(self,
                 amount: Decimal,
                 num_parts: int,
                 free_parts: int = 0):
        """
        :param installments:
            Número de parcelas suportadas.
        :param free_installments:
            Número de parcelas livres de juros.
        """
        self.amount = amount

        if num_parts <= 1:
            num_parts = 1

        if free_parts <= 1:
            free_parts = 1

        self.num_parts = num_parts
        self.free_parts = free_parts

    def get_installment_prices(self):
        """ Resgata lista de preços finais a sererem pagos no parcelamento. """
        interests_amount = self._get_interest_amount()

        prices = [self.amount]
        for part in range(2, self.num_parts + 1):
            part_amount = self.amount / part
            if part > self.free_parts:
                part_amount += part * interests_amount

            prices.append(part_amount)

        return prices

    def get_installment_interests_amounts(self):
        """ Regata somente valores de juros cobrados no parcelamento. """
        interests_amount = self._get_interest_amount()

        prices = [0.00]

        for part in range(2, int(self.num_parts) + 1):
            part_amount = 0.00

            if part > self.free_parts:
                part_amount = part * interests_amount

            prices.append(part_amount)

        return prices

    def get_installment_interests_amount(self):
        """ Resgata valor de juros a ser pago ao final do parcelamento. """
        if self.num_parts == 1:
            return self.amount

        return self._get_interest_amount() * self.num_parts

    def _get_interest_amount(self):
        return self.amount * self.interests_rate

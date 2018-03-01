from code import interact
from decimal import Decimal


class Calculator(object):
    """
    Cálculo de transação a ser feita pelo Pagarme sempre levando em
    conta 2 recebedores.
    """
    interests = Decimal(0.0229)

    def __init__(self, installments=1, free_installments=0):
        """
        :param installments:
            Número de parcelas suportadas.
        :param free_installments:
            Número de parcelas livres de juros.
        """
        self.installments = int(installments)
        self.free_installments = free_installments

    def get_installments(self, amount):
        """ Resgata lista de parcelas. """
        amount = self._normalize_amount(amount)
        interests_amount = round(amount * self.interests, 2)

        prices = [amount]
        for part in range(1, int(self.installments) + 1):
            if part <= 1:
                continue

            part_amount = amount / part
            if part > self.free_installments:
                part_amount += part * interests_amount

            prices.append(round(part_amount, 2))

        return prices

    def get_liquid_interest_prices(self, amount):
        amount = self._normalize_amount(amount)
        interests_amount = round(amount * self.interests, 2)

        prices = [0.00]

        for part in range(1, int(self.installments) + 1):
            if part <= 1:
                continue

            part_amount = 0.00

            if part > self.free_installments:
                part_amount = part * interests_amount

            prices.append(round(part_amount, 2))

        return prices

    def get_installment_interest(self, amount, installments=1):
        amount = self._normalize_amount(amount)
        if installments <= 1:
            return round(amount, 2)

        interests = amount * self.interests
        return round(Decimal(interests * installments), 2)

    def get_receiver_amount(self, amount, percent, installments=1):
        """
        Resgata valor a ser processado na transação para o primeiro recebedor.
        Lembrando que ele é responsável pelo pagamento de impostos:
            - charge_processing_fee
            - charge_remainder_fee

        :param amount:
            Montante a ser transacionado.
        :param percent:
            Percentual a ser calculado para o recebedor
        :param absorb_tax:
            Se o cálculo deve levar em consideração a absorvação da taxa
            de transação, substraindo do montante relativo ao percentual do
            recebedor.
        :param installments:
            Número de parcelamentos da transação.
        :return:
        """
        if not percent:
            percent = Decimal(100)

        if not isinstance(percent, Decimal):
            percent = Decimal(percent) / 100

        amount = self._normalize_amount(amount)
        interests_amount = amount * self.interests

        percent_amount = amount * percent

        if 1 < installments <= self.free_installments:
            percent_amount -= installments * interests_amount

        return round(percent_amount, 2)

    @staticmethod
    def _normalize_amount(amount):
        if not isinstance(amount, Decimal):
            amount = Decimal(Decimal(amount) / 100)
        return amount

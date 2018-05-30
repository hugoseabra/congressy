from decimal import Decimal
from collections import Iterable


class Calculator(object):
    """
    Calculadora que processa preços de cálculos de juros em diferentes
    cenários: informando valores de acordo com um montante, juros absorvidos
    e valores de juros separadamente.
    """
    def __init__(self,
                 interests_rate: Decimal,
                 total_installments=1,
                 free_installments=0):
        """
        :param installments:
            Número de parcelas suportadas.
        :param free_installments:
            Número de parcelas livres de juros.
        """
        self.interests_rate = interests_rate
        self.total_installments = int(total_installments)
        self.free_installments = int(free_installments)

    def get_installment_prices(self, amount: Decimal) -> list:
        """ Resgata lista de valores de parcelas. """
        interests_amount = amount * self.interests_rate

        prices = [amount]
        for part in range(1, int(self.total_installments) + 1):
            if part <= 1:
                continue

            part_amount = amount / part
            if part > self.free_installments:
                part_amount += interests_amount

            prices.append(part_amount)

        return prices

    def get_installment_totals(self, amount: Decimal) -> list:
        """ Resgata lista de valores de parcelas. """

        total_prices = []
        parts = 1
        for price in self.get_installment_prices(amount):
            total_prices.append(price * parts)
            parts += 1

        return total_prices

    def get_liquid_interest_prices(self, amount: Decimal) -> list:
        """ Resgata lista de valores de juros por parcela. """
        interests_amount = amount * self.interests_rate

        prices = [0.00]

        for part in range(1, int(self.total_installments) + 1):
            if part <= 1:
                continue

            part_amount = 0.00

            if part > self.free_installments:
                part_amount = part * interests_amount

            prices.append(part_amount)

        return prices

    def get_installment_total_amount(self,
                                     amount: Decimal,
                                     installments=1) -> Decimal:
        """ Resgata montante total do valor líquido + juros. """
        if installments > self.total_installments:
            raise Exception(
                'Parcelamento inforamdo ultrapassa a quantidade de parcelas'
                ' permitidas.'
            )

        total_prices = self.get_installment_totals(amount)
        return total_prices[installments - 1]

    def get_installment_part_amount(self,
                                 amount: Decimal,
                                 installments=1) -> Decimal:
        """ Resgata valor de acordo com a parcela informada. """
        if installments > self.total_installments:
            raise Exception(
                'Parcelamento inforamdo ultrapassa a quantidade de parcelas'
                ' permitidas.'
            )

        part_prices = self.get_installment_prices(amount)
        return part_prices[installments-1]

    def get_installment_interests_amount(self,
                                 amount: Decimal,
                                 installments=1) -> Decimal:
        """ Resgata valor de juros de acordo com a parcela informada. """
        if installments > self.total_installments:
            raise Exception(
                'Parcelamento inforamdo ultrapassa a quantidade de parcelas'
                ' permitidas.'
            )

        part_prices = self.get_liquid_interest_prices(amount)
        return part_prices[installments-1]

    def get_absorbed_interests_amount(self,
                                      amount: Decimal,
                                      installments=1) -> Decimal:
        """
        Resgata o valor de juros absorvido quando o número de parcelas
        está livre de juros.
        """
        # se não parcelamento ou se o número de parcelas não está dentro do
        # número de parcelas livres de juros
        if installments <= 1 or installments > self.free_installments:
            return Decimal(0.00)

        interests_amount = amount * self.interests_rate
        return Decimal(interests_amount * installments)


class InstallmentResult(object):
    """
    Resultado de cálculos de parcelamento de um valor total de diversos itens
    comercializados.
    """
    def __init__(self,
                 calculator: Calculator,
                 amount: Decimal,
                 num_installments: int) -> None:
        self.calculator = calculator

        self.amount = amount
        self.num_installments = num_installments

    @property
    def part_amount(self) -> Decimal:
        """ Resgata montante da parcela. """
        return self.calculator.get_installment_part_amount(
            self.amount,
            self.num_installments
        )

    @property
    def total_amount(self) -> Decimal:
        """ Resgata valor total a ser pago. """
        return self.calculator.get_installment_total_amount(
            self.amount,
            self.num_installments
        )

    @property
    def interests_amount(self) -> Decimal:
        """ Resgata somente montante de juros. """
        return self.calculator.get_installment_interests_amount(
            self.amount,
            self.num_installments
        )

    @property
    def absorved_interests_amount(self):
        """ Resgata o montante de juros absorvido. """
        return self.calculator.get_absorbed_interests_amount(
            self.amount,
            self.num_installments
        )

    def __iter__(self):
        iters = {
            'num_installments': self.num_installments,
            'free_installments': self.calculator.free_installments,
            'interests_rate': self.calculator.interests_rate,
            'amount': self.amount,
            'part_amount': self.part_amount,
            'total_amount': self.total_amount,
            'interests_amount': self.interests_amount,
            'absorved_interests_amount': self.absorved_interests_amount,
        }

        for x, y in iters.items():
            yield x, y

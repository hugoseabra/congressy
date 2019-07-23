from datetime import date
from decimal import Decimal

from .payable_date import CreditCardPayableDate


class Payable:
    def __init__(self,
                 partial_amount: Decimal,
                 transaction_date: date,
                 fee_amount: Decimal = 0,
                 installment=1,
                 antecipation_fee_percent: Decimal = 0,
                 recipient_id: str = None):
        """

        :param partial_amount: Valor parcial da recebível antes de subtrair
            taxas
        :param transaction_date: Data da transação
        :param fee_amount: Valor da taxa de transação
        :param installment: Número da parcela
        :param antecipation_fee_percent: Taxa mensal percentual de antecipação
            de pagamento.
        :param recipient_id: ID do recebedor
        """
        if installment < 1:
            installment = 1

        self.partial_amount = partial_amount
        self.transaction_date = transaction_date
        self.fee_amount = fee_amount
        self.installment = installment
        self.antecipation_fee_percent = antecipation_fee_percent
        self.recipient_id = recipient_id

        payable_date = CreditCardPayableDate(self.transaction_date)
        self.payment_date = payable_date.get_date(
            installment=installment,
            additional_business_days=2,
        )
        self.antecipation_date = payable_date.get_antecipation_date()

    def get_antecipation_amount(self,
                                antecipation_date: date = None) -> Decimal:

        if not antecipation_date:
            antecipation_date = self.antecipation_date

        if antecipation_date < self.transaction_date:
            raise Exception(
                'Data de antecipação é anterior à data da transação.'
                ' Data da transação: {}, Data de antecipação: {}'.format(
                    self.transaction_date,
                    antecipation_date,
                )
            )

        if antecipation_date > self.payment_date:
            return Decimal(0)

        # Taxa diária de antecipação. Padrão de 30 dias.
        fee_decimal_per_day = \
            (round(self.antecipation_fee_percent, 2) / 30) / 100

        amount = self.partial_amount - self.fee_amount
        fee_amount_per_day = amount * fee_decimal_per_day

        diff_dates = antecipation_date - self.payment_date
        fee_amount = Decimal(fee_amount_per_day * -diff_dates.days)

        return round(fee_amount, 2)

    def get_amount(self, antecipation_date: date = None) -> Decimal:
        amount = self.partial_amount - self.fee_amount
        antecipation_amount = self.get_antecipation_amount(antecipation_date)
        return round(amount - antecipation_amount, 2)

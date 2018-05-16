from decimal import Decimal

from payment.models import Transaction


class PaymentReportCalculator(object):
    """
    Calcula valores monetários de pagamentos de uma determinada inscrição.
    """

    def __init__(self, subscription):
        self.queryset = Transaction.objects.filter(subscription=subscription)
        self.subscription = subscription

        self.lots = {}
        self.transactions = {}
        self.full_prices = {}
        self.dividend_amount = round(Decimal(0.00), 2)
        self.total_paid = round(Decimal(0.00), 2)
        self.installments = {}
        self.has_manual = {}

        self._fetch_lots()
        self._fetch_transactions()
        self._set_dividend_amount()

    def get_transactions(self):
        return self.queryset

    def _fetch_lots(self):
        """
        Os lotes que existem nas transações são as inscriçõs que o usuário
        fez eventualmente na plataforma e criou transações com elas.
        """
        for trans in self.queryset.order_by(
                'lot__name',
                'subscription__created'):

            lot = trans.lot
            if not lot.price or not trans.amount:
                continue

            price = lot.get_calculated_price()

            self.lots[lot.pk] = lot
            # Calculo reverso para refletir o fluxo de caixa:
            # O valor de inscrição é um DÉBITO do fluxo.
            self.full_prices[lot.pk] = -price

            if trans.installments > 1:
                parts_amount = round((trans.amount / trans.installments), 2)
                interests_amount = round((trans.amount - price), 2)
                self.installments[lot.pk] = {
                    'interests_amount': interests_amount,
                    'amount': parts_amount,
                    'num': trans.installments
                }

            if trans.manual is True and lot.pk not in self.has_manual:
                self.has_manual[lot.pk] = True

        for lot_pk, installment in self.installments.items():
            self.full_prices[lot.pk] -= installment['interests_amount']

    def _fetch_transactions(self):
        transactions = {}
        for pk, lot in self.lots.items():
            if not lot.price:
                continue

            transactions[lot.pk] = []

        queryset = self.queryset.order_by(
            'date_created',
            'subscription__created',
        )

        for trans in queryset:
            transactions[trans.lot.pk].append(trans)

            if trans.status == trans.PAID:
                # Calculo reverso para refletir o fluxo de caixa:
                # O pagamento é um CRÉDITO do fluxo.
                self.full_prices[trans.lot.pk] += trans.amount
                self.total_paid += trans.amount

        self.transactions = transactions

    def _set_dividend_amount(self):
        for lot_pk, amount in self.full_prices.items():
            self.dividend_amount += amount

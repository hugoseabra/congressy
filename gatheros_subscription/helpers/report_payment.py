from decimal import Decimal

from payment.models import Transaction


class PaymentReportCalculator(object):
    """
    Calcula valores monetários de pagamentos de uma determinada inscrição.
    """

    def __init__(self, subscription):
        self.queryset = Transaction.objects.filter(
            subscription=subscription,
            lot_id=subscription.lot_id
        )
        self.subscription = subscription
        self.current_lot = subscription.lot

        self.lots = {}
        self.transactions = {}
        self.full_prices = {}
        self.dividend_amount = round(Decimal(0.00), 2)
        self.total_paid = round(Decimal(0.00), 2)
        self.installments = {}
        self.has_manual = {}
        self.is_subscription_confirmed = False

        self._fetch_lots()
        self._fetch_transactions()
        self._set_dividend_amount()
        self._set_subscription_confirmation()

    def get_transactions(self):
        return self.queryset

    def _fetch_lots(self):
        """
        Os lotes que existem nas transações são as inscrições que o usuário
        fez eventualmente na plataforma e criou transações com elas.
        """
        if self.queryset.count():
            for trans in self.queryset.order_by(
                    'lot__name',
                    'subscription__created'):

                if trans.lot_id == self.current_lot.pk:
                    continue

                lot = trans.lot

                self.lots[lot.pk] = lot

                if trans.status != Transaction.WAITING_PAYMENT:
                    price = trans.amount

                    # Calculo reverso para refletir o fluxo de caixa:
                    # O valor de inscrição é um DÉBITO do fluxo.
                    self.full_prices[lot.pk] = -price

                    if trans.installments > 1:
                        parts_amount = \
                            round((trans.amount / trans.installments), 2)
                        interests_amount = round((trans.amount - price), 2)
                        self.installments[lot.pk] = {
                            'interests_amount': interests_amount,
                            'amount': parts_amount,
                            'num': trans.installments
                        }

                    if trans.manual is True and lot.pk not in self.has_manual:
                        self.has_manual[lot.pk] = True

                    for lot_pk, installment in self.installments.items():
                        self.full_prices[lot.pk] -= \
                            installment['interests_amount']

                else:
                    # Calculo reverso para refletir o fluxo de caixa:
                    # O valor de inscrição é um DÉBITO do fluxo.
                    self.full_prices[lot.pk] = -(lot.get_calculated_price())

        if self.current_lot.pk not in self.lots:
            self.lots[self.current_lot.pk] = self.current_lot

        if self.current_lot.pk not in self.full_prices:
            self.full_prices[self.current_lot.pk] = \
                -(self.current_lot.get_calculated_price())

    def _fetch_transactions(self):
        transactions = {}
        for pk in self.lots.keys():
            # if not lot.price:
            #     continue
            transactions[pk] = []

        queryset = self.queryset.order_by(
            'date_created',
            'subscription__created',
        )

        if not queryset.count():
            self.full_prices[self.current_lot.pk] = \
                -(self.current_lot.get_calculated_price())
            return

        for trans in queryset:

            manual = trans.manual is True
            waiting_payment = trans.status == Transaction.WAITING_PAYMENT
            manual_waiting = \
                trans.manual_payment_type == Transaction.MANUAL_WAITING_PAYMENT

            is_waiting = waiting_payment and manual is False

            transactions[trans.lot.pk].append(trans)

            if is_waiting is False and manual and manual_waiting:
                continue

            if is_waiting is False and trans.status == Transaction.PAID:
                # Calculo reverso para refletir o fluxo de caixa:
                # O pagamento é um CRÉDITO do fluxo.
                self.full_prices[trans.lot_id] += trans.amount
                self.total_paid += trans.amount

        self.transactions = transactions

    def _set_dividend_amount(self):
        for lot_pk, amount in self.full_prices.items():
            self.dividend_amount += amount

    def _set_subscription_confirmation(self):
        """
        Inscrição está confirmada quando não há dividendos ou está em ver com
        o evento e há pelo menos algum valor pago.
        """
        self.is_subscription_confirmed = \
            self.total_paid > 0 and self.dividend_amount >= 0

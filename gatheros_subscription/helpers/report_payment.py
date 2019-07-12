from decimal import Decimal

from django.utils.formats import localize

from payment.models import Transaction


class PaymentReportCalculator(object):
    """
    Calcula valores monetários de pagamentos de uma determinada inscrição.
    """

    def __init__(self, subscription):
        self.queryset = Transaction.objects.filter(
            subscription_id=subscription.pk,
        )
        self.subscription = subscription
        self.current_lot = subscription.ticket_lot

        self.lots = list()

        self.debt_amounts = dict()
        self.tax_amounts = dict()
        self.paid_amounts = dict()

        self.total_debts = Decimal(0)
        self.total_paid = Decimal(0)
        self.total_taxes = Decimal(0)
        self.cash_amount = Decimal(0)
        self.amount_to_pay = Decimal(0)

        self.installments = dict()
        self.is_subscription_confirmed = False

        self._set_debt_amounts()
        self._fetch_payment_amounts()
        self._set_total_amounts()

        self._set_subscription_confirmation()

    def get_transactions(self):
        return self.queryset

    def _set_debt_amounts(self):
        """
        Busca todos os débitos da inscrição
        """
        lot = self.current_lot

        self.lots.append(lot)

        if lot.pk not in self.debt_amounts:
            self.debt_amounts[lot.pk] = list()

        self.debt_amounts[lot.pk].append({
            'name': 'Inscrição: {}'.format(lot.name),
            'created_on': self.subscription.created,
            'description': self.subscription.code,
            'amount': lot.get_subscriber_price()
        })

        addon_serv_qs = self.subscription.subscription_services.filter(
            optional__ticket_id=lot.ticket_id,
            optional__liquid_price__gt=0,
        )

        addon_prod_qs = self.subscription.subscription_services.filter(
            optional__ticket_id=lot.ticket_id,
            optional__liquid_price__gt=0,
        )

        for sub_service in addon_serv_qs:
            optional = sub_service.optional

            self.debt_amounts[lot.pk].append({
                'name': 'Atividade extra: {}'.format(optional.name),
                'created_on': self.subscription.created,
                'description': 'Tipo: {} <br /> Grupo temático: {}'.format(
                    optional.optional_type.name,
                    optional.theme.name,
                ),
                'amount': optional.price
            })

        for sub_service in addon_prod_qs:
            optional = sub_service.optional

            self.debt_amounts[lot.pk].append({
                'name': 'Atividade extra: {}'.format(optional.name),
                'created_on': self.subscription.created,
                'description': 'Tipo: {}'.format(optional.optional_type.name),
                'amount': optional.price
            })

    def _fetch_payment_amounts(self):
        """
        Busca todos os débitos da inscrição
        """
        queryset = self.queryset.filter(status=Transaction.PAID)

        if queryset.count() == 0:
            return

        for trans in queryset:

            lot = trans.ticket_lot

            if lot not in self.lots:
                self.lots.append(lot)

            if lot.pk not in self.debt_amounts:
                self.debt_amounts[lot.pk] = list()

            if lot.pk not in self.paid_amounts:
                self.paid_amounts[lot.pk] = list()

            if lot.pk not in self.tax_amounts:
                self.tax_amounts[lot.pk] = list()

            self.paid_amounts[lot.pk].append({
                'created_on': trans.date_created,
                'transaction': trans,
                'amount': trans.amount,
                'manual': trans.manual is True,
                'manual_type':
                    trans.manual_payment_type if trans.manual is True else '',
                'manual_author':
                    trans.manual_author if trans.manual is True else '',
            })

            price = lot.get_subscriber_price()

            if trans.installments > 1 and trans.amount > price:

                if lot.pk not in self.installments:
                    self.installments[lot.pk] = []

                interests_amount = round((price - trans.amount), 2)

                if interests_amount:
                    self.tax_amounts[lot.pk].append({
                        'name': 'Taxas de parcelamento',
                        'created_on': trans.date_created,
                        'description': '{}x R$ {}'.format(
                            trans.installments,
                            localize(trans.installment_amount),
                        ),
                        'amount': interests_amount,
                    })

    def _set_total_amounts(self):
        for lot_pk, items in self.paid_amounts.items():
            for item in items:
                self.total_paid += item.get('amount')
                self.cash_amount += item.get('amount')

        for lot_pk, items in self.debt_amounts.items():
            for item in items:
                self.total_debts += item.get('amount')
                self.cash_amount -= item.get('amount')

        for lot_pk, items in self.tax_amounts.items():
            for item in items:
                self.total_taxes += item.get('amount')

        self.amount_to_pay = -self.cash_amount

    def _set_subscription_confirmation(self):
        """
        Inscrição está confirmada quando não há dividendos ou está em ver com
        o evento e há pelo menos algum valor pago.
        """
        self.is_subscription_confirmed = self.cash_amount >= 0

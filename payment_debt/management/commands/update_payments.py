from decimal import Decimal

from django.core.management.base import BaseCommand

from gatheros_event.event_state import EventPayable
from gatheros_event.models import Event
from payment.models import Payment, Transaction
from payment_debt.models import Debt


class Command(BaseCommand):
    help = 'Cria pagamentos vinculados a inscrições que tiveram transações.'

    def handle(self, *args, **options):

        total_nodebts = 0
        total_payments = 0
        total_debts = 0

        subs_notransctions = []

        for event in Event.objects.all():
            if is_paid_event(event) is False:
                continue

            for sub in event.subscriptions.all():
                if sub.free is True:
                    continue

                transactions = sub.transactions.filter(
                    status=Transaction.PAID
                )

                if not transactions:
                    subs_notransctions.append(sub)
                    continue

                debts = sub.debts.all()

                if not debts:
                    total_nodebts += 1

                else:
                    debt = debts.first()

                for transaction in transactions:
                    lot = transaction.lot
                    cash_type = self._get_cash_type(transaction)

                    try:
                        transaction.payment
                        continue

                    except AttributeError:
                        pass

                    payment = Payment(
                        lot=lot,
                        subscription=sub,
                        manual=transaction.manual,
                        manual_author=transaction.manual_author,
                        cash_type=cash_type,
                        amount=transaction.amount,
                        paid=transaction.paid,
                        transaction=transaction,
                    )

                    payment.save()

                    total_payments += 1

                    if not debts:
                        continue

                    if debt.amount:
                        # Caso já tiver valor registrado, ignorar pendência.
                        # Há casos em que houve mais de um pagamento para
                        # diferentes lotes. Se houver, haverá diversos
                        # pagamentos para um pendência só, e vamos descobrir
                        # quem está com crédito.
                        continue

                    if transaction.installments == 1:
                        interests_amount = 0
                        installment_amount = transaction.amount

                    elif transaction.installments > 1:

                        if not transaction.installment_amount:
                            installment_amount = \
                                transaction.amount / transaction.installments
                        else:
                            installment_amount = transaction.installment_amount

                        interests_amount = \
                            transaction.amount - lot.get_calculated_price()

                        if interests_amount < 0:
                            interests_amount = 0

                    debt.amount = transaction.amount
                    debt.liquid_amount = transaction.liquid_amount
                    debt.installments = transaction.installments
                    debt.installment_amount = installment_amount
                    debt.installment_interests_amount = interests_amount

                    if transaction.paid is True:
                        debt.status = Debt.DEBT_STATUS_PAID

                    debt.save()
                    total_debts += 1

        self.stdout.write('------------------------')
        self.stdout.write(self.style.WARNING(
            'Paid subscriptions without transactions: {}'.format(
                len(subs_notransctions)
            )
        ))
        self.stdout.write(self.style.WARNING(
            'Paid subscriptions without debts: {}'.format(total_nodebts)
        ))
        self.stdout.write(self.style.SUCCESS(
            'Payments created: {}'.format(total_payments)
        ))
        self.stdout.write(self.style.SUCCESS(
            'Debts updated: {}'.format(total_debts)
        ))

        self.stdout.write('------------------------')
        self.stdout.write('Adjusting debts without transactions:')

        total_debts = 0

        for sub in subs_notransctions:
            if sub.free is True:
                continue

            event = sub.event
            lot = sub.lot

            debts = sub.debts.all()

            if not debts:
                continue

            debt = debts.first()

            if debt.amount and debt.liquid_amount:
                continue

            amount = lot.get_calculated_price()
            liquid_amount = lot.price

            cgsy_percent = Decimal(event.congressy_percent) / 100
            percent_amount = lot.price * cgsy_percent
            if lot.transfer_tax is True:
                liquid_amount = lot.price
                amount = lot.price + percent_amount

            else:
                amount = lot.price
                liquid_amount = lot.price - percent_amount

            debt.amount = amount
            debt.liquid_amount = liquid_amount
            debt.installments = 1
            debt.installment_amount = amount
            debt.installment_interests_amount = Decimal(0)
            debt.save()

            total_debts += 1

        self.stdout.write(self.style.SUCCESS(
            'Debts ajusted: {}'.format(total_debts)
        ))

    def _get_cash_type(self, transaction):
        trans_type = transaction.type

        cash_type = None

        if trans_type == Transaction.CREDIT_CARD:
            cash_type = Payment.CASH_TYPE_CREDIT_CARD

        elif trans_type == Transaction.BOLETO:
            cash_type = Payment.CASH_TYPE_BOLETO

        elif transaction.manual is True:
            manual_type = transaction.manual_payment_type

            if manual_type == Transaction.MANUAL_PAYMENT_MONEY:
                cash_type = Payment.CASH_TYPE_MONEY

            elif manual_type == Transaction.MANUAL_PAYMENT_PAYCHECK:
                cash_type = Payment.CASH_TYPE_PAYCHECK

            elif manual_type == Transaction.MANUAL_PAYMENT_DEBIT_CARD:
                cash_type = Payment.CASH_TYPE_DEBIT_CARD

            elif manual_type == Transaction.MANUAL_PAYMENT_CREDIT_CARD:
                cash_type = Payment.CASH_TYPE_CREDIT_CARD

            elif manual_type == Transaction.MANUAL_PAYMENT_BANK_DEPOSIT:
                cash_type = Payment.CASH_TYPE_BANK_DEPOSIT

            elif manual_type == Transaction.MANUAL_PAYMENT_BANK_TRANSFER:
                cash_type = Payment.CASH_TYPE_TRANSFER

        return cash_type

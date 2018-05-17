from decimal import Decimal

from django.core.management.base import BaseCommand

from payment.models import Transaction


class Command(BaseCommand):
    help = 'Updates the existing transactions installments and installments ' \
           'price'

    def handle(self, *args, **options):

        all_transactions = Transaction.objects.all()

        updated = 0
        updated_credit_card_data = 0
        total = all_transactions.count()

        for transaction in all_transactions:
            trx = transaction.data

            if trx and 'installments' in trx \
                    and trx['installments'] \
                    and int(trx['installments']) \
                    and (not transaction.installments or
                         not transaction.installment_amount):
                updated += 1
                amount = str(trx['amount'])
                size = len(amount)
                cents = amount[-2] + amount[-1]
                amount = '{}.{}'.format(amount[0:size - 2], cents)
                amount = Decimal(amount)

                installments = int(trx['installments'])
                transaction.installments = installments
                transaction.installment_amount = \
                    round((amount / installments), 2)

                if transaction.type == Transaction.CREDIT_CARD:
                    transaction.credit_card_holder = trx['card_holder_name']
                    transaction.credit_card_first_digits = \
                        trx['card_first_digits']
                    transaction.credit_card_last_digits = \
                        trx['card_last_digits']
                    updated_credit_card_data += 1

                transaction.save()
                msg = 'Updated transaction id: {}'.format(transaction.pk)
                self.stdout.write(self.style.SUCCESS(msg))

        msg = 'Total transactions: {}'.format(total)
        self.stdout.write(self.style.SUCCESS(msg))
        msg = 'Updated  total transactions: {}'.format(updated)
        self.stdout.write(self.style.SUCCESS(msg))
        msg = 'Updated {} credit card data'.format(updated_credit_card_data)
        self.stdout.write(self.style.SUCCESS(msg))

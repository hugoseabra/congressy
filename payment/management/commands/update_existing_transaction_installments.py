from decimal import Decimal

from django.core.management.base import BaseCommand

from payment.models import Transaction


class Command(BaseCommand):
    help = 'Updates the existing transactions installments and installments ' \
           'price'

    def handle(self, *args, **options):

        all_transactions = Transaction.objects.all()

        updated = 0
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

                transaction.save()
                msg = 'Updated transaction id: {}'.format(str(transaction.pk))
                self.stdout.write(
                    self.style.SUCCESS(msg))

        msg = 'Total transactions: {}'.format(str(total))
        self.stdout.write(self.style.SUCCESS(msg))
        msg = 'Updated  total transactions: {}'.format(str(updated))
        self.stdout.write(self.style.SUCCESS(msg))

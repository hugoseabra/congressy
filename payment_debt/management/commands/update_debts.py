from decimal import Decimal

from django.core.management.base import BaseCommand

from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from payment_debt.models import Debt, DebtConfig


class Command(BaseCommand):
    help = 'Cria pendências vinculadas a inscrições com lotes pagos.'

    def handle(self, *args, **options):

        total_events = 0
        total_debts = 0
        total_subs = 0

        events = Event.objects.all()

        for event in events:
            if self._has_paid_lots(event) is False:
                continue

            debts_created = 0
            for sub in event.subscriptions.all():
                if sub.free is True:
                    continue

                lot = sub.lot

                if sub.debts.count() > 0:
                    continue

                debt = Debt.objects.create(
                    subscription=sub,
                    type=Debt.DEBT_TYPE_SUBSCRIPTION,
                    status=Debt.DEBT_STATUS_DEBT,
                )

                DebtConfig.objects.create(
                    debt=debt,
                    transfer_tax=lot.transfer_tax,
                    interests_rate=Decimal(2.29),
                    total_installments=lot.installment_limit,
                    free_installments=lot.num_install_interest_absortion,
                )
                debts_created += 1
                total_subs += 1

            if debts_created == 0:
                continue

            total_debts += debts_created
            total_events += 1

            if len(event.name) > 25:
                event_name = event.name[0:25]
            else:
                event_name = event.name

            self.stdout.write("  - {}: {}".format(
                event_name,
                self.style.SUCCESS(debts_created)
            ))

        self.stdout.write('------------------------')
        self.stdout.write(self.style.SUCCESS(
            'Total events: {}'.format(total_events)
        ))
        self.stdout.write(self.style.SUCCESS(
            'Total subscriptions: {}'.format(total_subs)
        ))
        self.stdout.write(self.style.SUCCESS(
            'Total debts: {}'.format(total_debts)
        ))


    def _has_paid_lots(self, event):
        for lot in event.lots.all():
            if not lot.price:
                continue

            return True

        return False

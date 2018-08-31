from django.core.management.base import BaseCommand

from gatheros_event.event_state import EventPayable
from gatheros_event.models import Event
from payment_debt.models import Debt


class Command(BaseCommand):
    help = 'Cria pendências vinculadas a inscrições com lotes pagos.'

    def handle(self, *args, **options):

        total_events = 0
        total_debts = 0
        total_subs = 0

        events = Event.objects.all()

        for event in events:
            if EventPayable().is_satisfied_by(event) is False:
                continue

            debts_created = 0
            for sub in event.subscriptions.all():
                if sub.free is True:
                    continue

                if sub.debts.count() > 0:
                    continue

                Debt.objects.create(
                    subscription=sub,
                    type=Debt.DEBT_TYPE_SUBSCRIPTION,
                    status=Debt.DEBT_STATUS_DEBT,
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

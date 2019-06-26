from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q

from attendance.models import AttendanceService, Checkin, Checkout
from core.cli.mixins import CliInteractionMixin
from gatheros_event.models import Person
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin
from gatheros_subscription.models import Subscription
from payment.models import Transaction, TransactionStatus


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = "Coleta registros editados e/ou criados a partir de uma" \
           " data e hora."

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')
        parser.add_argument('date_start', type=str, nargs='?',
                            help='Informa no formato: YYYY-MM-DD')

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        date_start_str = options.get('date_start')
        if date_start_str:
            date_start = datetime.strptime(date_start_str, '%Y-%m-%d')

        else:
            date_start = event.date_start
            self.stdout.write(self.style.WARNING(
                'Data incial do evento como referência: {}'.format(
                    date_start.replace(hour=0, minute=0, second=0)
                )
            ))

        date_start = date_start.replace(hour=0, minute=0, second=0)
        print('==============================================================')
        self.collect_subscriptions_and_persons(event, date_start)
        self.collect_transactions_and_statuses(event, date_start)
        self.collect_attendance_services(event, date_start)
        self.collect_checkins(event, date_start)
        self.collect_checkouts(event, date_start)

    def collect_subscriptions_and_persons(self, event, date_start):
        collection = Subscription.objects.filter(
            Q(created__gte=date_start) | Q(modified__gte=date_start),
            event_id=event.pk,
        )
        self._collect_data('gatheros_subscription.subscription', collection)

        person_pks = [sub.person_id for sub in collection]
        persons = Person.objects.filter(
            Q(created__gte=date_start) | Q(modified__gte=date_start),
            pk__in=person_pks
        )
        self._collect_data('gatheros_event.person', persons)

    def collect_transactions_and_statuses(self, event, date_start):
        collection = Transaction.objects.filter(
            date_created__gte=date_start,
            lot__event_id=event.pk,
        )
        self._collect_data('payment.transaction', collection)

        trans_pks = [t.pk for t in collection]
        collection = TransactionStatus.objects.filter(
            transaction_id__in=trans_pks,
        )
        self._collect_data('payment.transactionstatus', collection)

    def collect_attendance_services(self, event, date_start):
        collection = AttendanceService.objects.filter(
            Q(created_on__gte=date_start) | Q(modified_on__gte=date_start),
            event_id=event.pk,
        )
        self._collect_data('attendance.attendanceservice', collection)

    def collect_checkins(self, event, date_start):
        collection = Checkin.objects.filter(
            created_on__gte=date_start,
            attendance_service__event_id=event.pk,
        )
        self._collect_data('attendance.checkin', collection)

    def collect_checkouts(self, event, date_start):
        collection = Checkout.objects.filter(
            created_on__gte=date_start,
            checkin__attendance_service__event_id=event.pk,
        )
        self._collect_data('attendance.checkout', collection)

    def _collect_data(self, name, collection):
        num_records = len(collection)

        print()
        self.stdout.write(
            '{}: {} registros'.format(
                name,
                self.style.SUCCESS(str(num_records))
            )
        )

        self.progress_bar(
            0,
            num_records,
            prefix='Progress:',
            suffix='Complete',
            length=40
        )
        processed = 0

        # gatheros_event.person
        for item in collection:
            # Força sincronização mesmo sem alterar o registro.
            item.sync_force = True
            item.save()
            processed += 1

            self.progress_bar(
                processed,
                num_records,
                prefix='Progress:',
                suffix='Complete',
                length=40
            )

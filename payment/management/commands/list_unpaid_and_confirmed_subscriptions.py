from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Sum

from attendance.helpers.attendance import subscription_is_checked
from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin
from gatheros_subscription.models import Subscription
from payment.models import Transaction


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = 'Lista inscrições confirmadas e não pagas.'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')

    def handle(self, *args, **options):
        subs = Subscription.objects.filter(
            test_subscription=False,
            completed=True,
            status=Subscription.CONFIRMED_STATUS,
            lot__price__gt=0,
        )
        if options.get('event_id'):
            event = self._get_event(pk=options.get('event_id'))

            subs = subs.filter(event_id=event.pk)

        should_be_pending_subs = list()

        for sub in subs:
            to_be_paid = sub.lot.get_calculated_price()
            paid = self.paid_amount(sub)

            if not paid or (paid < to_be_paid):
                self._print_subscription(sub,
                                         self.is_checked_in(sub),
                                         to_be_paid,
                                         paid)
                should_be_pending_subs.append(sub)

        if should_be_pending_subs and \
                self.confirmation_yesno('Alterar status?', default=False):
            for sub in should_be_pending_subs:
                sub.status = Subscription.AWAITING_STATUS
                sub.save()
            self.stdout.write(self.style.SUCCESS('Feito!'))

    def paid_amount(self, sub: Subscription):
        trans = Transaction.objects.filter(
            subscription_id=sub.pk,
            status=Transaction.PAID,
        ).aggregate(total_amount=Sum('amount'))
        return trans['total_amount']

    def is_checked_in(self, sub):
        return subscription_is_checked(sub.pk)

    def _print_subscription(self, subscription: Subscription,
                            checked_in: bool,
                            to_pay_amount: Decimal,
                            paid_amount: Decimal):
        self.stdout.write(self.style.SUCCESS(
            " Atualizando inscrição:\n"
            "    - PK: {}\n"
            "    - Evento: {} ({})\n"
            "    - Lote: {} ({})\n"
            "    - Participante: {} (ID: {})\n"
            "    - E-mail: {}\n"
            "    - Criação: {}\n"
            "    - Modificação: {}\n"
            "    - Origem: {}\n"
            "    - Presente: {}\n"
            "    - A pagar: {}\n"
            "    - Pago: {}\n".format(
                subscription.pk,
                subscription.event.name,
                subscription.lot.name,
                subscription.lot_id,
                subscription.event_id,
                subscription.person.name,
                subscription.person_id,
                subscription.person.email,
                subscription.created.strftime('%d/%m/%Y %Hh%M'),
                subscription.modified.strftime('%d/%m/%Y %Hh%M'),
                subscription.get_origin_display(),
                'Sim' if checked_in is True else 'Não',
                to_pay_amount,
                paid_amount,
            )
        ))

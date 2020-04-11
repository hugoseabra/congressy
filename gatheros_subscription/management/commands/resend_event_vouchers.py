from django.core.management.base import BaseCommand

from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin
from gatheros_subscription.models import Subscription
from mailer.services import notify_new_free_subscription


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = 'Reenvia vouchers de inscrições de um evento.'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')
        parser.add_argument(
            '--force-internal',
            dest='force_internal',
            action='store_true',
            help='processar em simulação, mas sem executar na persistência.',
        )

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        subs_qs = Subscription.objects.filter(
            event_id=event.pk,
            test_subscription=False,
            status=Subscription.CONFIRMED_STATUS,
        )

        if options.get('force_internal', False) is False:
            subs_qs = subs_qs.filter(origin=Subscription.DEVICE_ORIGIN_MANAGE)

        subs_qs = subs_qs.order_by('person__email')

        self.stdout.write(self.style.SUCCESS(
            '# ENVIOS: {}'.format(subs_qs.count() or '0')
        ))

        counter = 1
        for sub in subs_qs:
            notify_new_free_subscription(event=sub.event, subscription=sub)
            self.stdout.write(self.style.SUCCESS(
                '{}. - Enviado para "{}". Person: {}, Insc: {}'.format(
                    counter,
                    sub.person.email,
                    sub.person.pk,
                    sub.pk
                )
            ))
            counter += 1

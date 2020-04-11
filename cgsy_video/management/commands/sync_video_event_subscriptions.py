from django.core.management.base import BaseCommand

from cgsy_video import workers
from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin
from gatheros_subscription.models import Subscription


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = "Sincroniza inscrições de um evento no microsserviço de vídeos."

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        for sub in event.subscriptions.all():
            workers.sync_subscriber.delay(sub.pk)

        self.stdout.write(self.style.SUCCESS('Sincronização agendada'))
        self.stdout.write('')

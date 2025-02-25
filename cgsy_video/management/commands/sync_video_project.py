from django.core.management.base import BaseCommand

from cgsy_video import workers
from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = "Sincroniza project de um evento no microsserviço de vídeos."

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        workers.sync_project.delay(event.pk)
        self.stdout.write(self.style.SUCCESS('Sincronização agendada'))
        self.stdout.write('')

from django.core.management.base import BaseCommand

from cgsy_video import workers
from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = "Sincroniza toda configuração do evento no microsserviço de vídeos."

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        workers.sync_event_user.delay(event.pk)
        workers.sync_namespace.delay(event.pk)
        workers.sync_project.delay(event.pk)

        for sub in event.subscriptions.all():
            workers.sync_subscriber.delay(sub.pk)

        self.stdout.write(self.style.SUCCESS('Sincronizações agendada'))
        self.stdout.write('')

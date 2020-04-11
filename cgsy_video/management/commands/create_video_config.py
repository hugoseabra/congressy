from django.core.management.base import BaseCommand

from cgsy_video.models import VideoConfig
from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin

from cgsy_video import synchronizer

class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = "Cria configuração de vídeo para evento."

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        config = synchronizer.get_event_video_config(event)
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Event Video Config:'))

        self.stdout.write(self.style.SUCCESS(
            '\t - token: {}'.format(config.token)
        ))
        self.stdout.write(self.style.SUCCESS(
            '\t - project: {}'.format(config.project_pk)
        ))
        self.stdout.write('')
        self.stdout.write('')

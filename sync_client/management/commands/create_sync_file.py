import json
from datetime import datetime

from django.core.management.base import BaseCommand

from core.cli.mixins import CliInteractionMixin
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin
from sync.entity_keys import sync_file_keys
from sync_client.models import SyncItem


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = "Cria arquivo de sincronização usando os itens de sincronização" \
           " disponíveis."

    def handle(self, *args, **options):
        items = SyncItem.objects.all()

        content = dict()

        # Garantindo todas as chaves no conteúdo do arquivo
        for model_key in sync_file_keys:
            content[model_key] = []

        for item in items:
            if item.object_type not in content:
                content[item.object_type] = []
                print()
                self.stdout.write(self.style.SUCCESS(item.object_type.upper()))

            object_name = '\t- {} (ID: {})'.format(
                item.object_repr,
                item.object_id,
            )

            data = json.loads(item.content)
            data['process_type'] = item.process_type
            data['process_time'] = \
                item.process_time.strftime('%Y-%m-%d %H:%m:%s')

            self.stdout.write(object_name)
            content[item.object_type].append(data)

        now = datetime.now().strftime('%Y-%m-%d_%H%m%s')
        file_path = '/tmp/SyncFile_{}.json'.format(now)

        with open(file_path, 'w+') as f:
            f.write(json.dumps(content))
            f.close()

        print()
        self.stdout.write('Arquivo salvo em: {}'.format(file_path))
        print()

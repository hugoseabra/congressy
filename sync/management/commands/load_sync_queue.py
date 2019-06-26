import json
import os
from collections import OrderedDict

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from core.cli.mixins import CliInteractionMixin
from sync.entity_keys import sync_file_keys
from sync.models import SyncQueue


class Command(BaseCommand, CliInteractionMixin):
    help = "Carrega item de sincronização que está aguardando na fila."

    def handle(self, *args, **options):
        item = self.get_item()

        sync_file_path = os.path.join(
            settings.MEDIA_ROOT,
            str(item.file_path),
        )

        if not os.path.exists(sync_file_path):
            self.stderr.write('Arquivo não existe: {}'.format(sync_file_path))
            self.exit()

        all_data = json.load(open(sync_file_path))

        ordered_data = OrderedDict()

        for model_key in sync_file_keys:
            for key, items in all_data.items():
                if key not in model_key:
                    continue

                ordered_data[model_key] = items

        additions = OrderedDict()
        num_additions = 0

        editions = OrderedDict()
        num_editions = 0

        deletions = OrderedDict()
        num_deletions = 0

        self.stdout.write('REGISTROS:')
        for key, items in ordered_data.items():
            # data_item = serializers.deserialize("json", data)
            self.stdout.write(' {}: {}'.format(
                self.style.SUCCESS(str(len(items)).zfill(5)),
                key
            ))

            if key not in additions:
                additions[key] = list()

            if key not in editions:
                editions[key] = list()

            if key not in deletions:
                deletions[key] = list()

            for i in items:
                if i['process_type'] == 'addition':
                    num_additions += 1
                    additions[key].append(i)

                elif i['process_type'] == 'edition':
                    num_editions += 1
                    editions[key].append(i)

                elif i['process_type'] == 'deletion':
                    num_deletions += 1
                    deletions[key].append(i)

        print()

        self.stdout.write('AÇÕES DE REGISTRO:')
        self.stdout.write('     Novos: {}'.format(
            self.style.SUCCESS(str(num_additions)))
        )
        self.stdout.write('   Edições: {}'.format(
            self.style.SUCCESS(str(num_editions)))
        )
        self.stdout.write(' Exclusões: {}'.format(
            self.style.SUCCESS(str(num_deletions)))
        )

        print()

        self.confirmation_yesno('Continuar?', default=False)

        with atomic():
            if num_additions:
                print()
                self.stdout.write('ADICIONANDO REGISTROS:')
                self.process(additions.items(), process_type='save')

            if num_editions:
                print()
                self.stdout.write('EDITANDO REGISTROS:')
                self.process(editions.items(), process_type='save')

                print()

            if num_deletions:
                print()
                self.stdout.write('EXCLUINDO REGISTROS:')
                self.process(deletions.items(), process_type='delete')

                print()

    def get_item(self):
        items = SyncQueue.objects.filter(
            status=SyncQueue.NOT_STARTED_STATUS,
            client__active=True,
        )

        choice_items = [(str(item), item) for item in items]

        sync_item = self.choice_list('item',
                                     'Selecione um item da fila',
                                     choice_items)

        return sync_item['item']

    def process(self, collection, process_type='save'):
        for key, items in collection:
            print()
            num = len(items)

            self.stdout.write('{}: {}'.format(
                self.style.SUCCESS(key),
                num,
            ))
            data_json = json.dumps(items)

            self.progress_bar(
                0,
                num,
                prefix='Progress:',
                suffix='Complete',
                length=40
            )
            processed = 0

            for item in serializers.deserialize("json", data_json):
                if process_type == 'save':
                    item.save()
                elif process_type == 'delete':
                    item.delete()
                else:
                    raise Exception('No process type provided')

                processed += 1

                self.progress_bar(
                    processed,
                    num,
                    prefix='Progress:',
                    suffix='Complete',
                    length=40
                )

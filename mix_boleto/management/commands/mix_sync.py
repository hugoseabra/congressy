from datetime import datetime, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand

from gatheros_event.models import Event, Category
from mix_boleto.mix.sync import MixSync
from mix_boleto.models import SyncResource


class Command(BaseCommand):
    help = 'Sincroniza inscrições entre MixEvents e Congressy'

    def handle(self, *args, **options):
        call_command('loaddata', 'sync_resource')

        resource = SyncResource.objects.first().alias

        # event = Event.objects.create(
        #     organization_id=741,
        #     name='Event: Maroto',
        #     date_start=datetime.now() + timedelta(days=15),
        #     date_end=datetime.now() + timedelta(days=19),
        #     category=Category.objects.first(),
        # )
        #
        # event_pk = event.pk
        event_pk = 424
        print(event_pk)

        synchronizer = MixSync(
            resource_alias=resource,
            event_id=event_pk,
        )

        synchronizer.prepare()
        synchronizer.run()

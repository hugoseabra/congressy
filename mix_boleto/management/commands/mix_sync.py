from django.core.management.base import BaseCommand

from mix_boleto.mix.sync import MixSync
from mix_boleto.models import SyncResource


class Command(BaseCommand):
    help = 'Sincroniza inscrições entre MixEvents e Congressy'

    def handle(self, *args, **options):
        resource = SyncResource.objects.first().alias
        event_pk = 444

        synchronizer = MixSync(
            resource_alias=resource,
            event_id=event_pk,
        )

        synchronizer.prepare()
        synchronizer.run()

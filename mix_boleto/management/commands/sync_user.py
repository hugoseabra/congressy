from django.core.management.base import BaseCommand

from gatheros_event.models import Event
from mix_boleto.mix import MixSync
from mix_boleto.models import SyncResource


class Command(BaseCommand):
    help = 'Atualiza Congressy com Mix de um usuário específico.'

    def add_arguments(self, parser):
        parser.add_argument('resource_alias', type=str)
        parser.add_argument('event_id', type=int)
        parser.add_argument('mix_subscription_id', type=int)

    def handle(self, *args, **options):

        resource_alias = options.get('resource_alias')
        event_id = options.get('event_id')
        mix_subscription_id = options.get('mix_subscription_id')

        if not event_id:
            msg = 'Hook de sincronização entre MixEvents e' \
                  ' Congressy - event_id não encontrado.'

            self.stderr.write(self.style.ERROR(msg))
            return

        if not resource_alias:
            msg = 'Hook de sincronização entre MixEvents e Congressy -' \
                  ' resource_alias não encontrado.'

            self.stderr.write(self.style.ERROR(msg))
            return

        if not mix_subscription_id:
            msg = 'Hook de sincronização entre MixEvents e Congressy -' \
                  ' mix_subscription_id não encontrado.'

            self.stderr.write(self.style.ERROR(msg))
            return

        event = Event.objects.get(pk=int(event_id))
        sync_resource = SyncResource.objects.get(alias=str(resource_alias))

        synchronizer = MixSync(
            resource_alias=sync_resource.alias,
            event_id=event.pk,
        )

        synchronizer.prepare(mix_subscription_id=mix_subscription_id)
        synchronizer.run()

        msg = 'Sincronizada realizada com sucesso!'
        self.stderr.write(self.style.ERROR(msg))

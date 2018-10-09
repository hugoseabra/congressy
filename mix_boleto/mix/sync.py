from mix_boleto.mix.connection import MixConnection
from mix_boleto.models import SyncResource
from .subscription_collection_builder import MixSubscriptionCollectionBuilder


class MixSync(object):
    """
        Essa classe é responsavel por preparar e executar a criação de
        inscrições e sincronização com banco de dados da MixEvents.
    """

    def __init__(self, resource_alias: str, event_id: int, ) -> None:
        """

        :param resource_alias:
        :param event_id:
        """
        self.event_id = event_id
        self.mix_subscriptions = list()
        credentials = SyncResource.objects.get(alias=resource_alias)
        self.connection = MixConnection(
            sync_resource_id=credentials.pk,
            host=credentials.host,
            db_name=credentials.db_name,
            user=credentials.user,
            password=credentials.password,
        )

    def prepare(self):
        builder = MixSubscriptionCollectionBuilder(
            event_id=self.event_id,
            db=self.connection,
        )

        self.mix_subscriptions = builder.build()

    def run(self):
        for subscription in self.mix_subscriptions:
            subscription.sync_all()

        self.connection.close()

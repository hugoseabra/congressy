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

            Construtor

        :param resource_alias: string identificadora de recurso
        :param event_id: um inteiro como chave primaria de um evento
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

    def prepare(self) -> None:
        """
            Responsavel por construir todos os artefatos necessarios para a
            execução da sincronização

        :return: None
        """
        builder = MixSubscriptionCollectionBuilder(
            event_id=self.event_id,
            db=self.connection,
        )

        self.mix_subscriptions = builder.build()

    def run(self) -> None:
        """
            Responsavel por executar a sincronização

        :return: None
        """
        for subscription in self.mix_subscriptions:
            subscription.sync_all()

        self.connection.close()

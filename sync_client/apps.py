from django.apps import AppConfig


class SyncClientConfig(AppConfig):
    name = 'sync_client'
    verbose_name = "Cliente de sincronização"

    # noinspection PyUnresolvedReferences
    def ready(self):
        import sync_client.signals

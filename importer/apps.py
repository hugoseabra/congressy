from django.apps import AppConfig


class ImporterConfig(AppConfig):
    name = 'importer'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import importer.signals


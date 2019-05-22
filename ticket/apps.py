from django.apps import AppConfig


class TicketConfig(AppConfig):
    name = 'ticket'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import ticket.signals

from gatheros_event.models import Event
from gatheros_subscription.models import FormConfig
from service_tags.models import CustomServiceTag
from gatheros_event.event_specifications.visible import EventVisible

class CurrentEventState(object):
    def __init__(self, event: Event) -> None:
        self.event = event
        self.slug = event.slug
        self.organization = event.organization

        self.custom_service_tag = self._get_custom_script_tags()
        self.info = self._get_info()
        self.form_config = self._get_form_config()
        self.period = event.get_period()

        self.bank_account_configured = \
            self.organization.is_bank_account_configured()
        self.active_bank_account_configured = \
            self.organization.active_recipient

        self.public_tickets = list()
        self.private_tickets = list()

    def _get_info(self):
        if hasattr(self.event, 'info') and self.event.info is not None:
            return self.event.info

        return None

    def _get_form_config(self):
        has_form_config = hasattr(self.event, 'formconfig')
        if has_form_config and self.event.formconfig is not None:
            return self.event.formconfig

        return FormConfig(event=self.event)

    def _get_custom_script_tags(self):
        if hasattr(self.event, 'custom_service_tag') and \
                        self.event.custom_service_tag is not None:
            return self.event.custom_service_tag

        return CustomServiceTag(event=self.event)

    def get_ticket_queryset(self):
        return self.event.tickets.order_by('name')

    def get_public_tickets(self):
        if self.public_tickets:
            return self.public_tickets

        queryset = self.get_ticket_queryset().filter(private=False,
                                                      active=True)
        self.public_tickets = [
            ticket
            for ticket in queryset
            if ticket.running is True
        ]
        return self.public_tickets

    def get_private_tickets(self):
        if self.private_tickets:
            return self.private_tickets

        queryset = self.get_ticket_queryset().filter(private=True,
                                                      active=True)
        self.private_tickets = [
            ticket
            for ticket in queryset
            if ticket.running is True
        ]
        return self.private_tickets

    def get_all_tickets(self):
        return self.get_ticket_queryset().filter(active=True)

    def get_available_tickets(self):
        return self.get_public_tickets() + self.get_private_tickets()

    def get_paid_tickets(self):
        return [
            ticket
            for ticket in self.get_ticket_queryset()
            if ticket.price > 0
        ]

    def has_available_tickets(self):
        return len(self.get_available_tickets()) > 0

    def has_available_private_tickets(self):
        return len(self.get_private_tickets()) > 0

    def has_available_public_tickets(self):
        return len(self.get_public_tickets()) > 0

    def has_paid_tickets(self):
        """ Retorna se evento possui algum lote pago. """
        return len(self.get_paid_tickets()) > 0

    def has_coupon(self):
        """ Retorna se possui cupom, seja qual for. """
        for ticket in self.get_private_tickets():
            # código de exibição
            if ticket.private and ticket.exhibition_code:
                return True

        return False

    def subscription_enabled(self):
        if self.has_available_tickets() is False:
            return False

        return self.event.status == Event.EVENT_STATUS_NOT_STARTED

    def is_private_event(self):
        """ Verifica se evento Ã© privado possuindo apenas lotes privados. """
        public_tickets = self.get_public_tickets()
        private_tickets = self.get_private_tickets()
        return len(public_tickets) == 0 and len(private_tickets) > 0

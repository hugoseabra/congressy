from gatheros_event.models import Event
from gatheros_subscription.models import FormConfig
from service_tags.models import CustomServiceTag


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

        self._lot_statuses = {}

        self.public_lots = []
        self.private_lots = []

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

    def is_lot_running(self, lot):
        status = self.get_lot_status(lot)
        return status == lot.LOT_STATUS_RUNNING

    def get_lots_queryset(self):
        return self.event.lots.order_by('date_end', 'name', 'price')

    def get_public_lots(self):
        if self.public_lots:
            return self.public_lots

        queryset = self.get_lots_queryset().filter(private=False, active=True)
        self.public_lots = [
            lot
            for lot in queryset
            if self.is_lot_running(lot)
        ]
        return self.public_lots

    def get_private_lots(self):
        if self.private_lots:
            return self.private_lots

        queryset = self.get_lots_queryset().filter(private=True, active=True)
        self.private_lots = [
            lot
            for lot in queryset
            if self.is_lot_running(lot)
        ]
        return self.private_lots

    def get_all_lots(self):
        return self.get_public_lots() + self.get_private_lots()

    def get_paid_lots(self):
        paid_lots = []
        for lot in self.get_all_lots():
            if lot.price and lot.price > 0:
                paid_lots.append(lot)

        return paid_lots

    def get_lot_status(self, lot):
        if lot.pk not in self._lot_statuses:
            self._lot_statuses[lot.pk] = lot.status

        return self._lot_statuses[lot.pk]

    def has_available_lots(self):
        lots = self.get_all_lots()
        return len(lots) > 0

    def has_available_private_lots(self):
        lots = self.get_private_lots()
        return len(lots) > 0

    def has_available_public_lots(self):
        lots = self.get_public_lots()
        return len(lots) > 0

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        return len(self.get_paid_lots()) > 0

    def has_coupon(self):
        """ Retorna se possui cupom, seja qual for. """
        for lot in self.get_private_lots():
            # código de exibição
            if lot.private and lot.exhibition_code:
                return True

        return False

    def subscription_enabled(self):
        if self.has_available_lots() is False:
            return False

        return self.event.status == Event.EVENT_STATUS_NOT_STARTED

    def subscription_finished(self):
        for lot in self.get_all_lots():
            if self.is_lot_running(lot):
                return False

        return True

    def is_private_event(self):
        """ Verifica se evento é privado possuindo apenas lotes privados. """
        public_lots = self.get_public_lots()
        private_lots = self.get_private_lots()
        return len(public_lots) == 0 and len(private_lots) > 0

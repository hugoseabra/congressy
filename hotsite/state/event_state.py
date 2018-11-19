from datetime import datetime

from audience.models import Lot as AudienceLot, AudienceCategory
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

        self.lots = list()

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

        assert isinstance(lot, AudienceLot), "is not a AudienceLot instance"

        return AudienceLot.objects.filter(
            id=lot.id,
            audience_category__event_id=self.event.id,
            date_start__lte=datetime.now(),
            date_end__gte=datetime.now(),
        ).exists()

    def get_lots(self):

        if self.lots:
            return self.lots

        for category in AudienceCategory.objects.filter(
                active=True,
                event=self.event,
        ):

            lot = category.current_lot
            if lot:
                self.lots.append(lot)

        return self.lots

    def get_paid_lots(self):

        paid_lots = list()

        for lot in self.get_lots():

            if lot.price and lot.price > 0:
                paid_lots.append(lot)

        return paid_lots

    def has_available_lots(self):



        return len(self.get_lots()) > 0

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        return len(self.get_paid_lots()) > 0

    def subscription_enabled(self):
        if self.has_available_lots() is False:
            return False

        return self.event.status == Event.EVENT_STATUS_NOT_STARTED

    def subscription_finished(self):
        for lot in self.get_lots():
            if self.is_lot_running(lot):
                return False

        return True

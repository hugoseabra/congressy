from .event.delete import EventDeleteView
from .event.list import EventListView
from .event.form import (
    EventAddFormView,
    EventEditFormView,
    EventPublicationFormView,
    EventSubscriptionTypeFormView,
    EventDatesFormView,
)
from .event.panel import EventPanelView
from .organization.switch import OrganizationSwitch
from .organization.panel import OrganizationPanelView
from .organization.invite import InviteView

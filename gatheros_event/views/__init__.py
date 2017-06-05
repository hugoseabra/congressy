from .event.delete import EventDeleteView
from .event.detail import (
    EventDetailView,
)
from .event.form import (
    EventAddFormView,
    EventDatesFormView,
    EventEditFormView,
    EventPublicationFormView,
    EventSubscriptionTypeFormView
)
from .event.list import EventListView
from .event.panel import EventPanelView
from .organization.invite import (
    InvitationCreateSuccessView,
    InvitationCreateView,
    InvitationDecisionView,
    InvitationProfileView
)
from .organization.panel import OrganizationPanelView
from .organization.switch import OrganizationSwitch

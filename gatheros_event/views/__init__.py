
# INVITATION
from gatheros_event.views.invite import (
    InvitationListView,
    InvitationCreateView,
    InvitationDecisionView,
    # InvitationProfileView,
)

# EVENT
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
from .event.info import EventInfoView
from .event.list import EventListView
from .event.panel import EventPanelView

# ORGANIZATION
from .organization.delete import OrganizationDeleteView
from .organization.form import (
    OrganizationAddFormView,
    OrganizationEditFormView,
)
from .organization.list import OrganizationListView
from .organization.panel import OrganizationPanelView
from .organization.switch import OrganizationSwitch

# PLACE
from .place.delete import PlaceDeleteView
from .place.form import (
    PlaceAddFormView,
    PlaceEditFormView,
)
from .place.list import PlaceListView

# PROFILE
from .profile import ProfileCreateView, ProfileView

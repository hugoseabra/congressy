""" Views """

# EVENT
from gatheros_event.views.event.delete import EventDeleteView
from .event.detail import EventDetailView
from .event.form import (
    EventAddFormView,
    EventDatesFormView,
    EventEditFormView,
    EventPublicationFormView,
    EventSlugUpdaterView,
    EventSubscriptionTypeFormView,
)
from .event.hotsite import EventHotsiteView
from .event.info import EventInfoView
from .event.list import EventListView
from .event.panel import EventPanelView
from .event.transfer import EventTransferView
from .event.publishing import EventPublishView
# INVITATION
from .invite import (
    InvitationCreateView,
    InvitationDecisionView,
    InvitationDeleteView,
    InvitationListView,
    InvitationProfileView,
    InvitationResendView,
    MyInvitationsListView,
)
# MEMBER
from .member import MemberDeleteView, MemberListView, MemberManageView
# ORGANIZATION
from .organization.delete import OrganizationDeleteView
from .organization.form import (
    OrganizationAddFormView,
    OrganizationAddInternalFormView,
    OrganizationEditFormView,
    OrganizationFinancialEditFormView,
)
from .organization.list import OrganizationListView
from .organization.panel import (
    OrganizationCancelMembershipView,
    OrganizationPanelView,
)
from .organization.switch import OrganizationSwitch
# PLACE
from .place.delete import PlaceDeleteView
from .place.form import (
    PlaceAddFormView,
    PlaceEditFormView,
)
from .place.list import PlaceListView
# PROFILE
from .profile import (
    PasswordResetConfirmView,
    PasswordResetView,
    ProfileCreateView,
    ProfileView,
)

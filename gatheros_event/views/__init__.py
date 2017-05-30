from .event.delete import EventDeleteView
from .event.form import EventAddFormView, EventEditDatesFormView, \
    EventEditFormView, EventPatchFormView
from .event.list import EventListView
from .event.panel import EventPanelView
from .organization.invite import InviteAcceptView, InviteSuccessView, \
    InviteView
from .organization.panel import OrganizationPanelView
from .organization.switch import OrganizationSwitch

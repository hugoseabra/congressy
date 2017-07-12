""" gatheros_event urls """
# pylint: skip-file

from .event import urlpatterns_event
from .invitation import urlpatterns_private_invitation
from .me import urlpatterns_private_me
from .member import urlpatterns_member
from .organization import urlpatterns_organization
from .place import urlpatterns_place

urlpatterns = urlpatterns_event
urlpatterns += urlpatterns_private_invitation
urlpatterns += urlpatterns_private_me
urlpatterns += urlpatterns_member
urlpatterns += urlpatterns_organization
urlpatterns += urlpatterns_place

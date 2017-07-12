""" gatheros_subscription urls """
# pylint: skip-file

from .form import urlpatterns_form
from .field import urlpatterns_field
from .field_option import urlpatterns_field_option
from .lot import urlpatterns_lot
from .me import urlpatterns_me
from .subscription import urlpatterns_subscription

urlpatterns = urlpatterns_form
urlpatterns += urlpatterns_field
urlpatterns += urlpatterns_field_option
urlpatterns += urlpatterns_lot
urlpatterns += urlpatterns_me
urlpatterns += urlpatterns_subscription

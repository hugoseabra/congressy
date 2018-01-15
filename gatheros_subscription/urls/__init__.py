""" gatheros_subscription urls """
# pylint: skip-file


from .lot import urlpatterns_lot
from .me import urlpatterns_me
from .subscription import urlpatterns_subscription

urlpatterns = urlpatterns_lot
urlpatterns += urlpatterns_me
urlpatterns += urlpatterns_subscription

""" gatheros_subscription urls """
# pylint: skip-file


from .form_config import urlpatterns_formconfig
from .category import urlpatterns_category
from .lot import urlpatterns_lot
from .me import urlpatterns_me
from .subscription import urlpatterns_subscription
from .survey import urlpatterns_survey

urlpatterns = urlpatterns_formconfig
urlpatterns += urlpatterns_lot
urlpatterns += urlpatterns_category
urlpatterns += urlpatterns_me
urlpatterns += urlpatterns_subscription
urlpatterns += urlpatterns_survey

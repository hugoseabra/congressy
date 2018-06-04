""" gatheros_subscription urls """
# pylint: skip-file
from rest_framework import routers


from gatheros_subscription import viewsets

router = routers.DefaultRouter()
router.register(r'lots', viewsets.LotViewSet)

urlpatterns = router.urls

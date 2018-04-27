# pylint: skip-file

from rest_framework import routers
from addon import viewsets

router = routers.DefaultRouter()

router.register(r'addon/optionals/services', viewsets.ServiceViewSet)
router.register(r'addon/optionals/products', viewsets.ProductViewSet)

urlpatterns = router.urls

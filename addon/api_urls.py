""" gatheros_subscription urls """
# pylint: skip-file
from rest_framework import routers


from addon import viewsets

router = routers.DefaultRouter()
router.register(r'products', viewsets.ProductViewSet)

urlpatterns = router.urls

""" gatheros_subscription urls """
# pylint: skip-file
from rest_framework import routers


from addon import viewsets

router = routers.DefaultRouter()

router.register(r'themes', viewsets.ThemeViewSet)
router.register(r'optional-types', viewsets.OptionalTypeViewSet)

router.register(r'products', viewsets.ProductViewSet)
router.register(r'subscription-service', viewsets.SubscriptionProductViewSet)

router.register(r'services', viewsets.ServiceViewSet)
router.register(r'subscription-services', viewsets.SubscriptionServiceViewSet)

urlpatterns = router.urls

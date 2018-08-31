# pylint: skip-file

from rest_framework import routers

from addon import viewsets

router = routers.DefaultRouter()

router.register(r'addon/optionals/services', viewsets.ServiceViewSet)
router.register(r'addon/optionals/products', viewsets.ProductViewSet)

router.register(
    r'addon/subscriptions/(?P<subscription_pk>[0-9A-Fa-f-]+)'
    r'/optionals/services',
    viewsets.SubscriptionServiceViewSet
)
router.register(
    r'addon/subscriptions/(?P<subscription_pk>[0-9A-Fa-f-]+)'
    r'/optionals/products',
    viewsets.SubscriptionProductViewSet
)

urlpatterns = router.urls

""" gatheros_subscription urls """
# pylint: skip-file
from rest_framework import routers
from django.conf.urls import include, url
from addon import viewsets

router = routers.DefaultRouter()

router.register(r'themes', viewsets.ThemeViewSet)
router.register(r'optional-types', viewsets.OptionalTypeViewSet)


urlpatterns = [
    url(r'^addon/optionals/services/$', viewsets.ServiceViewSet.as_view(),
        name="services-list"),
]

# router.register(r'products', viewsets.ProductViewSet)
# router.register(r'subscription-service', viewsets.SubscriptionProductViewSet)
# router.register(r'subscription-services', viewsets.SubscriptionServiceViewSet)

urlpatterns += router.urls

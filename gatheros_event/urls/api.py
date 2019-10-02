from rest_framework import routers

from gatheros_event import viewsets

router = routers.DefaultRouter()

router.register(r'peoples',
                viewsets.PersonViewSet,
                base_name="person",)

router.register(r'event/organizations',
                viewsets.OrganizationReadOnlyViewSet,
                base_name="organization",)

router.register(r'event/events',
                viewsets.EventReadOnlyViewSet,
                base_name="event",)

urlpatterns = router.urls

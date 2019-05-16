from rest_framework import routers

from gatheros_event import viewsets

router = routers.DefaultRouter()

router.register(r'event/events', viewsets.EventReadOnlyViewSet, base_name="event", )

urlpatterns = router.urls

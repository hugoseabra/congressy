from rest_framework import routers

from gatheros_event import viewsets

router = routers.DefaultRouter()

router.register(r'event/organizations',
                viewsets.OrganizationReadOnlyViewSet,
                base_name="organization",)

urlpatterns = router.urls

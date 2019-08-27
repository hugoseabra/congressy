from django.conf.urls import url, include
from rest_framework import routers

from .views import CityListView

router = routers.DefaultRouter()
router.register(r'cities', CityListView)

urlpatterns = [
    url(r'^', include(router.urls)),
]

from django.conf.urls import url
from rest_framework import routers

from .views import CityListView, ZipCodeViewSet

router = routers.DefaultRouter()
router.register(r'city/cities', CityListView)

public_city_api_urls = [
    url(
        r'city/zip_code/(?P<zip_code_number>[^/.]+)/',
        ZipCodeViewSet.as_view({'get': 'list'}),
        name='city_zipcode_url'
    ),
]

urlpatterns = router.urls
urlpatterns += public_city_api_urls

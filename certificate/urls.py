from django.conf.urls import include, url
from rest_framework import routers

from certificate import views, viewsets

private_certificate_urls = [
    url(
        r'^',
        views.CertificadoView.as_view(),
        name='event-certificate'
    ),
]


router = routers.DefaultRouter()
router.register(r'certificates', viewsets.CertificateViewSet)

api_certificate_urls = [
    url(r'^certificates/', include(router.urls)),
]

urlpatterns_certificate_urls = [
    url(
        r'^events/(?P<event_pk>[\d]+)/certificate/',
        include(private_certificate_urls)
    )
]

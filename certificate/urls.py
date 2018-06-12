from django.conf.urls import include, url
from rest_framework import routers

from certificate import views, viewsets

private_certificate_urls = [

    url(
        r'^form/',
        views.CertificateFormView.as_view(),
        name='event-certificate-form'
    ),
    url(
        r'^',
        views.CertificateConfigView.as_view(),
        name='event-certificate-config'
    ),
]

private_subscription_certificate_urls = [
    url(
        r'^',
        views.CertificatePDFView.as_view(),
        name='event-certificate-pdf'
    ),
]

router = routers.DefaultRouter()
router.register(r'certificates', viewsets.CertificateViewSet)

api_certificate_urls = [
    url(r'^certificates/', include(router.urls)),
]

urlpatterns_certificate_urls = [
    url(
        r'^events/(?P<event_pk>[\d]+)/certificate/subscription/(?P<pk>['r'0-9A-Fa-f-]+)/',
        include(private_subscription_certificate_urls)
    ),
    url(
        r'^events/(?P<event_pk>[\d]+)/certificate/',
        include(private_certificate_urls)
    ),
    url(
        r'^events/(?P<event_pk>[\d]+)/',
        include(api_certificate_urls)
    ),
]

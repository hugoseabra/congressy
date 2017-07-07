# pylint: skip-file

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

from gatheros_event.urls.me import urlpatterns_public_me
from gatheros_event.urls.invitation import urlpatterns_public_invitation

url_admin = [url(r'^admin/', admin.site.urls)]

private_urls = [
    url(r'^', include('gatheros_subscription.urls', 'subscription')),
    url(r'^', include('gatheros_event.urls', 'event')),
    url(r'^', include('gatheros_front.urls', 'front'))
]

public_urls = [
    url(r'^', include(urlpatterns_public_me, 'public-me')),
    url(r'^', include(urlpatterns_public_invitation, 'public-invitation')),
]

urlpatterns = url_admin + private_urls

urlpatterns += static.static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)

urlpatterns += static.static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

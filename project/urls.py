# pylint: skip-file

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

from gatheros_event.urls.me import (
    urlpatterns_public_account,
    urlpatterns_public_password,
)
from gatheros_event.urls.invitation import urlpatterns_public_invitation

admin_urlpatterns = [url(r'^admin/', admin.site.urls)]

private_urlpatterns = [
    url(r'^', include('gatheros_subscription.urls', 'subscription')),
    url(r'^', include('gatheros_event.urls', 'event')),
    url(r'^', include('gatheros_front.urls', 'front')),
]

public_urls = urlpatterns_public_account
public_urls += urlpatterns_public_invitation
public_auth_urlpatterns = [url(r'^', include(public_urls, 'public'))]

public_urlpatterns = [
    url(r'^', include(public_urls, 'public')),

    # Patterns do Django não podem estar sob um 'namespace'
    url(r'^', include(urlpatterns_public_password)),
]

urlpatterns = admin_urlpatterns
urlpatterns += private_urlpatterns
urlpatterns += public_urlpatterns

urlpatterns += static.static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)

urlpatterns += static.static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

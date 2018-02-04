# pylint: skip-file

import os
from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

from gatheros_event.urls.invitation import urlpatterns_public_invitation
from gatheros_event.urls.me import (
    urlpatterns_public_account,
    urlpatterns_public_password,
)
from gatheros_front.urls import (
    urlpatterns_private as gatheros_front_private,
    urlpatterns_public as gatheros_front_public,
)
from hotsite.urls import urlpatterns_public_hotsite
from payment.urls import public_payment_urls


admin_urlpatterns = [url(r'^admin/', admin.site.urls)]

private_urlpatterns = [
    url(r'^manage/', include('gatheros_subscription.urls', 'subscription')),
    url(r'^manage/', include('gatheros_event.urls', 'event')),
    url(r'^manage/', include(gatheros_front_private, 'front')),
]

public_urls = gatheros_front_public
public_urls += urlpatterns_public_account
public_urls += urlpatterns_public_password
public_urls += urlpatterns_public_invitation
public_urls += urlpatterns_public_hotsite

public_auth_urlpatterns = [url(r'^', include(public_urls, 'public'))]

public_urlpatterns = [
    url(r'^', include(public_urls, 'public')),

    # Patterns do Django não podem estar sob um 'namespace'
    url(r'^', include(urlpatterns_public_password)),
]

# API
api_urls = [
    url(r'^', include('payment.urls', 'payment')),
    url(r'^', include('kanu_locations.urls', 'city')),
]

api_urlpatterns = [url(r'^api/', include(api_urls, 'api'))]

urlpatterns = admin_urlpatterns
urlpatterns += private_urlpatterns
urlpatterns += public_urlpatterns
urlpatterns += api_urlpatterns

urlpatterns += static.static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)

urlpatterns += static.static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

if settings.DEBUG:

    if os.environ.get('DJANGO_SETTINGS_MODULE') == 'project.settings.staging':
        urlpatterns += [url(r'^logs/', include('logtailer.urls')),]

    import debug_toolbar

    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

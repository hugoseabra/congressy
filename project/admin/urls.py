# pylint: skip-file

from django.conf import settings
from django.conf.urls import include, static, url
from django.views.generic import RedirectView

from gatheros_event.urls.me import (
    urlpatterns_public_account,
    urlpatterns_public_password,
)
from gatheros_front.urls import (
    urlpatterns_public as gatheros_front_public,
)

handler500 = 'project.views.handler500'

private_urlpatterns = [
    url(r'^', include('admin.urls', 'front')),
]

public_urls = gatheros_front_public
public_urls += urlpatterns_public_account
public_urls += urlpatterns_public_password

public_auth_urlpatterns = [url(r'^', include(public_urls, 'public'))]

public_urlpatterns = [
    url(r'^', include(public_urls, 'public')),

    # Patterns do Django não podem estar sob um 'namespace'
    url(r'^', include(urlpatterns_public_password)),
]

public_urlpatterns += [
    url(r'^captcha/', include('captcha.urls')),
]

if not settings.DEBUG:
    public_urlpatterns += [
        url(
            r'^$',
            RedirectView.as_view(
                url='https://congressy.com'
            ),
            name='root'
        ),
    ]

urlpatterns = private_urlpatterns
urlpatterns += public_urlpatterns

# ============================ STATIC CONFIG ================================ #
urlpatterns += static.static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)

urlpatterns += static.static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

# ========================== DEBUG ENVIRONMENT ============================== #
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

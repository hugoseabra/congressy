# pylint: skip-file

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.views.generic import RedirectView

from certificate.urls import urlpatterns_certificate_urls
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
from payment.urls import (
    private_payment_urls,
    urlpatterns_public_payments,
)
from raffle.urls import urlpatterns_private_raffles
from service_tags.urls import service_tags_urlpatterns

handler404 = 'project.views.handler404'
handler500 = 'project.views.handler500'

admin_urlpatterns = []

admin_urlpatterns += [
    url(r'^grapelli/', include('grappelli.urls')),
    url(r'^grappelli_custom_autocomplete/',
        include('django_grappelli_custom_autocomplete.urls')),
    url(r'^cgsy-admin18/doc/', include('django.contrib.admindocs.urls')),
    url(r'^cgsy-admin18/', admin.site.urls)
]

private_urlpatterns = [
    url(r'^manage/', include('attendance.urls', 'attendance')),
    url(r'^manage/', include('addon.urls', 'addon')),
    url(r'^manage/', include('scientific_work.urls', 'scientific_work')),
    url(r'^manage/', include('gatheros_subscription.urls', 'subscription')),
    url(r'^manage/', include('importer.urls', 'importer')),
    url(r'^manage/', include(urlpatterns_certificate_urls, 'certificate')),
    url(r'^manage/', include(urlpatterns_private_raffles, 'raffle')),
    # url(r'^manage/', include('bitly.urls', 'bitly')),
    url(r'^manage/', include('gatheros_event.urls', 'event')),
    url(r'^manage/', include(gatheros_front_private, 'front')),
    url(r'^manage/', include(private_payment_urls, 'payment')),
]

public_urls = gatheros_front_public
public_urls += service_tags_urlpatterns
public_urls += urlpatterns_public_account
public_urls += urlpatterns_public_password
public_urls += urlpatterns_public_invitation
public_urls += urlpatterns_public_payments
public_urls += urlpatterns_public_hotsite

public_auth_urlpatterns = [url(r'^', include(public_urls, 'public'))]

public_urlpatterns = [
    url(r'^captcha/', include('captcha.urls')),
    url(r'^healthcheck/', include('health_check.urls')),
    url(r'^$', RedirectView.as_view(url='/login/'), name='root'),
]

public_urlpatterns += [
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    url(r'^', include(public_urls, 'public')),

    # Patterns do Django não podem estar sob um 'namespace'
    url(r'^', include(urlpatterns_public_password)),
]

# API
api_urls = [
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^', include('gatheros_event.urls.api', 'event')),
    url(r'^', include('gatheros_subscription.api_urls', 'subscription')),
    url(r'^', include('addon.api_urls', 'addon')),
    url(r'^', include('attendance.api_urls', 'attendance')),
    url(r'^', include('mix_boleto.api_urls', 'mix_boleto')),
    url(r'^', include('payment.api_urls', 'payment')),
    url(r'^', include('installment.api_urls', 'installment')),
    url(r'^', include('kanu_locations.urls', 'city')),
    url(r'^', include('sync.api_urls', 'sync')),
]

api_urlpatterns = [url(r'^api/', include(api_urls, 'api'))]

urlpatterns = admin_urlpatterns
urlpatterns += private_urlpatterns
urlpatterns += public_urlpatterns
urlpatterns += api_urlpatterns

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

    if not hasattr(settings, 'STAGING'):
        import debug_toolbar

        urlpatterns = [
                          url(r'^__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns

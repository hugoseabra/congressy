# pylint: skip-file

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

url_admin = [url(r'^admin/', admin.site.urls)]

url_manager = [
    url(r'^manager/', include(
        'gatheros_subscription.urls',
        'gatheros_subscription'
    )),
    url(r'^manager/', include(
        'gatheros_event.urls',
        'gatheros_event'
    )),
]

url_front = [url(r'^', include('gatheros_front.urls', 'gatheros_front'))]

urlpatterns = url_admin + url_manager + url_front

urlpatterns += static.static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)

urlpatterns += static.static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

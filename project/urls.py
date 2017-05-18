# pylint: skip-file

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

urlpatterns = \
    [
        url(r'^admin/', admin.site.urls),
        url(r'^organizador/', include(
            'gatheros_event.urls',
            'gatheros_event'
        )),
        url(r'^', include('gatheros_front.urls', 'gatheros_front')),
    ]

urlpatterns += static.static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)

urlpatterns += static.static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

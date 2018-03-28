# pylint: skip-file

import os

from django.conf import settings
from django.conf.urls import include, static, url

handler500 = 'project.views.handler500'

urlpatterns = [
    url(r'^captcha/', include('captcha.urls')),
]

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

    if os.environ.get('DJANGO_SETTINGS_MODULE') == 'project.settings.staging':
        urlpatterns += [url(r'^logs/', include('logtailer.urls')), ]

    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

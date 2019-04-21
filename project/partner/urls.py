# pylint: skip-file

from django.conf import settings
from django.conf.urls import include, static, url

from partner.urls import urlpatterns_public_partner

handler404 = 'project.views.handler404'
handler500 = 'project.views.handler500'

urlpatterns = [
    url(r'^captcha/', include('captcha.urls')),
    url(r'^healthcheck/', include('health_check.urls')),
    url(r'^', include(urlpatterns_public_partner, 'public')),
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
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

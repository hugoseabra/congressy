# pylint: skip-file

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.contrib.auth import views

url_admin = [url(r'^admin/', admin.site.urls)]

url_manager = [
    url(
                r'^lembrar-senha/$',
                views.PasswordResetView.as_view(),
                name='password_reset'
            ),
            url(
                r'^lembrar-senha/completo/$',
                views.PasswordResetDoneView.as_view(),
                name='password_reset_done'
            ),
            url(
                r'^redefinir/'
                '(?P<uidb64>[0-9A-Za-z_\-]+)/'
                '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                views.PasswordResetConfirmView.as_view(),
                name='password_reset_confirm'
            ),

    url(
        r'^redefinir/completo/$',
        views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
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

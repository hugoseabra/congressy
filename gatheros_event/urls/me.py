from django.conf.urls import include, url

from gatheros_event import views
from django.contrib.auth import views as auth_views

private_urls = [
    url(
        r'^me/$',
        views.ProfileView.as_view(),
        name='profile'
    ),
    url(
        r'^me/invitations$',
        views.MyInvitationsListView.as_view(),
        name='my-invitations'
    ),
]

public_urls = [
    url(
        r'^create-account/$',
        views.ProfileCreateView.as_view(),
        name='profile_create'
    ),
    url(
        r'^remember-password/$',
        auth_views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    url(
        r'^remember-password/complete/$',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    url(
        r'^reset-password/'
        '(?P<uidb64>[0-9A-Za-z_\-]+)/'
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    url(
        r'^reset-password/complete/$',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
]

urlpatterns_private_me = [url(r'^', include(private_urls))]
urlpatterns_public_me = [url(r'^', include(public_urls))]

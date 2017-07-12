""" Urls de `Invitation` """
from django.conf.urls import include, url

from gatheros_event import views

public_urls = [
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/profile/$',
        views.InvitationProfileView.as_view(),
        name='invitation-profile'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/$',
        views.InvitationDecisionView.as_view(),
        name='invitation-decision'
    ),
]

private_urls = [
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/resend/$',
        views.InvitationResendView.as_view(),
        name='invitation-resend'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/delete/$',
        views.InvitationDeleteView.as_view(),
        name='invitation-delete'
    ),
    url(
        r'^add/$',
        views.InvitationCreateView.as_view(),
        name='invitation-add'
    ),
    url(
        r'^$',
        views.InvitationListView.as_view(),
        name='invitation-list'
    ),
]

urlpatterns_public_invitation = [
    url(r'^invitations/', include(public_urls)),
]

urlpatterns_private_invitation = [
    url(
        r'^organizations/(?P<organization_pk>[\d]+)/invitations/',
        include(private_urls)
    ),
]

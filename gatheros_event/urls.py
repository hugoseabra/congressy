# pylint: skip-file
from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views

url_event = [
    url(
        r'^(?P<pk>[\d]+)/info',
        views.EventInfoView.as_view(),
        name='event-info'
    ),
    url(
        r'^(?P<pk>[\d]+)/detail',
        views.EventDetailView.as_view(),
        name='event-detail'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/dates',
        views.EventDatesFormView.as_view(),
        name='event-edit-dates'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/subscription',
        views.EventSubscriptionTypeFormView.as_view(),
        name='event-edit-subscription_type'
    ),
    url(
        r'^(?P<pk>[\d]+)/subscription_type/$',
        views.EventPublicationFormView.as_view(),
        name='event-edit-publication'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.EventEditFormView.as_view(),
        name='event-edit'
    ),
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.EventDeleteView.as_view(),
        name='event-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/$',
        views.EventPanelView.as_view(),
        name='event-panel'
    ),
    url(
        r'^add/$',
        views.EventAddFormView.as_view(),
        name='event-add'
    ),
    url(
        r'^$',
        views.EventListView.as_view(),
        name='event-list'
    ),
    url(
        r'^',
        RedirectView.as_view(
            pattern_name='gatheros_event:event-list',
            permanent=False
        )
    ),
]

url_organization = [
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.OrganizationDeleteView.as_view(),
        name='organization-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.OrganizationEditFormView.as_view(),
        name='organization-edit'
    ),
    url(
        r'^add/$',
        views.OrganizationAddFormView.as_view(),
        name='organization-add'
    ),
    url(
        r'^(?P<pk>[\d]+)/$',
        views.OrganizationPanelView.as_view(),
        name='organization-panel'
    ),
    url(
        r'^switch/$',
        views.OrganizationSwitch.as_view(),
        name='organization-switch'
    ),
    url(
        r'^$',
        views.OrganizationListView.as_view(),
        name='organization-list'
    ),
]

url_place = [
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.PlaceDeleteView.as_view(),
        name='place-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/$',
        views.PlaceEditFormView.as_view(),
        name='place-edit'
    ),
    url(
        r'^add/$',
        views.PlaceAddFormView.as_view(),
        name='place-add'
    ),
    url(
        r'^$',
        views.PlaceListView.as_view(),
        name='place-list'
    ),
]

url_manager_invitation = [
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

url_invitation = [
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

url_profile = [
    url(
        r'^me/$',
        views.ProfileView.as_view(),
        name='profile'
    ),
]

urlpatterns = [
    url(r'^manager/', include(url_profile)),
    url(r'^invitations/', include(url_invitation)),
    url(r'^manager/events/', include(url_event)),
    url(r'^manager/organizations/', include(url_organization)),
    url(
        r'^manager/organizations/(?P<organization_pk>[\d]+)/places/',
        include(url_place)
    ),
    url(
        r'^manager/organizations/(?P<organization_pk>[\d]+)/invitations/',
        include(url_manager_invitation)
    ),
]

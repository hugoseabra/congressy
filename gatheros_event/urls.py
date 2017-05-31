from django.conf.urls import include, url

from . import views

url_event = [
    url(
        r'^(?P<pk>[\d]+)/edit/dates$',
        views.EventEditDatesFormView.as_view(),
        name='event-edit-dates'
    ),
    url(
        r'^(?P<pk>[\d]+)/patch/$',
        views.EventPatchFormView.as_view(),
        name='event-patch'
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
]

url_organization = [
    url(
        r'^switch/$',
        views.OrganizationSwitch.as_view(),
        name='organization-switch'
    ),
    url(
        r'^convite/(?P<pk>[0-9A-Fa-f-]+)/perfil/$',
        views.InvitationProfileView.as_view(),
        name='invitation-profile'
    ),
    url(
        r'^convite/(?P<pk>[0-9A-Fa-f-]+)/$',
        views.InvitationDecisionView.as_view(),
        name='invitation-decision'
    ),
    url(
        r'^convite-sucesso/$',
        views.InvitationCreateSuccessView.as_view(),
        name='invitation-success'
    ),
    url(
        r'^convite/$',
        views.InvitationCreateView.as_view(),
        name='invitation'
    ),
    url(
        r'^$',
        views.OrganizationPanelView.as_view(),
        name='organization-panel'
    ),
]

urlpatterns = [
    url(r'^events/', include(url_event)),
    url(r'^organizations/', include(url_organization)),
]

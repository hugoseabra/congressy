from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views

url_event = [
    url(
        r'^(?P<pk>[\d]+)/edit/dates',
        views.EventSimpleEditView.as_view(view_name='dates'),
        name='event-edit-dates'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/subscription',
        views.EventSimpleEditView.as_view(view_name='subscription_type'),
        name='event-edit-subscription_type'
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
        r'^switch/',
        views.OrganizationSwitch.as_view(),
        name='organization-switch'
    ),
    url(
        r'^convite/',
        views.InviteView.as_view(),
        name='organization-invite'
    ),
    url(
        r'^',
        views.OrganizationPanelView.as_view(),
        name='organization-panel'
    ),
]

urlpatterns = [
    url(r'^events/', include(url_event)),
    url(r'^organizations/', include(url_organization)),
]

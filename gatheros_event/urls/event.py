""" Urls de `Event` """
from django.conf.urls import include, url
from django.views.generic import RedirectView

from gatheros_event import views

urls = [
    url(
        r'^(?P<pk>[\d]+)/transfer/',
        views.EventTransferView.as_view(),
        name='event-transfer'
    ),
    url(
        r'^(?P<pk>[\d]+)/info/',
        views.EventInfoView.as_view(),
        name='event-info'
    ),
    url(
        r'^(?P<pk>[\d]+)/webpage/',
        views.EventHotsiteView.as_view(),
        name='event-hotsite'
    ),
    url(
        r'^(?P<pk>[\d]+)/webpage2/banner/',
        views.EventHotsiteBannerView.as_view(),
        name='event-hotsite-banner'
    ),
    url(
        r'^(?P<pk>[\d]+)/webpage2/',
        views.EventHotsite2View.as_view(),
        name='event-hotsite2'
    ),
    url(
        r'^(?P<pk>[\d]+)/detail/',
        views.EventDetailView.as_view(),
        name='event-detail'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/dates/',
        views.EventDatesFormView.as_view(),
        name='event-edit-dates'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/subscription/',
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
        r'^(?P<pk>[\d]+)/publish/',
        views.EventPublishView.as_view(),
        name='event-publish'
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
        r'^duplicate/(?P<pk>[\d]+)/$',
        views.EventDuplicateFormView.as_view(),
        name='event-duplicate'
    ),
    url(
        r'^slug/$',
        views.EventSlugUpdaterView.as_view(),
        name='event-slug'
    ),
    url(
        r'^$',
        views.EventListView.as_view(),
        name='event-list'
    ),
    url(
        r'^',
        RedirectView.as_view(
            pattern_name='event:event-list',
            permanent=False
        )
    ),
]

urlpatterns_event = [url(r'^events/', include(urls))]

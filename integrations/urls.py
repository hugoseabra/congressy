""" Urls dos opcionais """

from django.conf.urls import include, url

from . import views

urls = [
    url(
        r'^/mailchimp/',
        views.MailChimpIntegrationsView.as_view(),
        name='event-integrations-mailchimp'
    ),
    url(
        r'^/',
        views.EventIntegrationsView.as_view(),
        name='event-integrations'
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/integrations', include(urls)),
]

from django.conf.urls import include, url

from . import views

url_events = [
    url(
        r'^(?P<pk>[\d]+)/$',
        views.EventPanelView.as_view(),
        name='event-panel'
    ),
    url(
        r'^add/$',
        views.EventWizardView.as_view(
            condition_dict={
                'step2': views.add_new_place
            }),
        name='event-add'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.EventEditView.as_view(),
        name='event-edit'
    ),
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.EventDeleteView.as_view(),
        name='event-delete'
    ),
    url(
        r'^',
        views.EventListView.as_view(),
        name='event-list'
    ),
]

url_organization = [
    url(
        r'^switch/',
        views.OrganizationSwitch.as_view(),
        name='organization-switch'
    ),
]

urlpatterns = [
    url(r'^org/', include(url_organization)),
    url(r'^events/', include(url_events)),
]

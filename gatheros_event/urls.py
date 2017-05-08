from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^org/switch/$', views.OrganizationSwitch.as_view(), name='organization-switch'),
    url(r'^events/$', views.EventListView.as_view(), name='event-list'),
    url(r'^events/(?P<pk>[\d]+)/$', views.EventPanelView.as_view(),
        name='event-panel'),
    url(r'^events/add/$', views.EventAddView.as_view(), name='event-add'),
    url(r'^events/(?P<pk>[\d]+)/edit/$', views.EventAddView.as_view(),
        name='event-edit'),
    url(r'^events/(?P<pk>[\d]+)/delete/$', views.EventDeleteView.as_view(),
        name='event-delete'),
]

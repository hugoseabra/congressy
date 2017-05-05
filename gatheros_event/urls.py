from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^org/switch/$', views.OrganizationSwitch.as_view(), name='organization-switch'),
    url(r'^eventos/$', views.EventListView.as_view(), name='event-list'),
    url(r'^eventos/(?P<pk>[\d]+)/$', views.EventPanelView.as_view(), name='event-panel'),
    url(r'^eventos/(?P<pk>[\d]+)/edit/$', views.EventFormView.as_view(), name='event-edit'),
    url(r'^eventos/(?P<pk>[\d]+)/delete/$', views.EventDeleteView.as_view(), name='event-delete'),
]

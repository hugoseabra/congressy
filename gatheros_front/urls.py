from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views
from gatheros_event import views as event_views

urlpatterns = [
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^$', event_views.EventListView.as_view(), name='start'),
]

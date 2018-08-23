""" Urls de `Event` """
from django.conf.urls import include, url

from attendance import views

urls = [
    url(
        r'^add/$',
        views.AddAttendanceServiceView.as_view(),
        name='attendance-list-add'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/',
        views.EditAttendanceServiceView.as_view(),
        name='attendance-list-edit'
    ),
    url(
        r'^(?P<pk>[\d]+)/delete/',
        views.DeleteAttendanceServiceView.as_view(),
        name='attendance-list-delete'
    ),
    url(
        r'^$',
        views.ManageListAttendanceView.as_view(),
        name='manage-list-attendance'
    ),
    url(
        r'^(?P<pk>[\d]+)/attendance/(?P<subscription_pk>[0-9A-Fa-f-]+)$',
        views.AttendanceView.as_view(),
        name='attendance'
    ),
    url(
        r'^(?P<pk>[\d]+)/search/',
        views.SubscriptionAttendanceSearchView.as_view(),
        name='attendance-list-edit'
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/attendance-list/', include(urls))]

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
        r'^(?P<pk>[\d]+)/attendance/',
        views.AttendancePageSearchView.as_view(),
        name='attendance'
    ),
    url(
        r'^(?P<pk>[\d]+)/chekin-list/',
        views.CheckinListView.as_view(),
        name='checkin-list'
    ),
    url(
        r'^(?P<pk>[\d]+)/dashboard/',
        views.AttendanceDashboardView.as_view(),
        name='dashboard'
    ),
    url(
        r'^(?P<pk>[\d]+)/api/attendance/search/$',
        views.SubscriptionSearchViewSet.as_view(),
        name='subscription-api-attendance-search'
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/attendance-list/', include(urls))]

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
        r'^$',
        views.ManageListAttendanceView.as_view(),
        name='manage-list-attendance'
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/attendance-list/', include(urls))]

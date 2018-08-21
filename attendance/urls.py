""" Urls de `Event` """
from django.conf.urls import include, url

from attendance import views

urls = [
    url(
        r'^add/$',
        views.AddAttendanceServiceView.as_view(),
        name='attendance-list-add'
    ),
    # url(
    #     r'^$',
    #     views.LotListView.as_view(),
    #     name='lot-list'
    # ),
]

urlpatterns = [url(r'^events/(?P<event_pk>[\d]+)/attendance-list/', include(urls))]

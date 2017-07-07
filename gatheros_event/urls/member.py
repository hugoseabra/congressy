from django.conf.urls import include, url

from gatheros_event import views

urls = [
    url(
        r'^(?P<pk>[\d]+)/manage/$',
        views.MemberManageView.as_view(),
        name='member-manage'
    ),
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.MemberDeleteView.as_view(),
        name='member-delete'
    ),
    url(
        r'^$',
        views.MemberListView.as_view(),
        name='member-list'
    ),
]

urlpatterns_member = [
    url(
        r'^organizations/(?P<organization_pk>[\d]+)/members/',
        include(urls)
    ),
]

from django.conf.urls import url, include

from . import views

urls = [
    url(r'^add/$', views.WorkAddView.as_view(), name='work-add'),
    url(r'^list/$', views.WorkListView.as_view(), name='work-list'),
]

work_api_urls = [
    url(r'^$', views.WorkAPIListView.as_view(), name='api_work-list'),
    url(r'^(?P<pk>[\d]+)$', views.WorkAPIUpdateView.as_view(),
        name='api_work-update'),
]

urlpatterns = [
    url(r'^subscription/(?P<pk>[0-9A-Fa-f-]+)/scientific_work/',
        include(urls)),
    url(r'^api/scientific_work/', include(work_api_urls)),

]

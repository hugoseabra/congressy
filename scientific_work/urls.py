from django.conf.urls import include, url

from . import views

urls = [
    url(r'^add/$', views.WorkAddView.as_view(), name='work-add'),
    url(r'^list/$', views.WorkListView.as_view(), name='work-list'),
]

urlpatterns = [
    url(r'^subscription/(?P<subscription_pk>[0-9A-Fa-f-]+)/scientific_work/',
        include(urls))
]

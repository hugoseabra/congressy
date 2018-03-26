from django.conf.urls import include, url

from bitly import views

urls = [
    url(
        r'^$',
        views.BitlyView.as_view(),
        name='lot-list'
    ),
]

urlpatterns = [url(r'^events/(?P<event_pk>[\d]+)/bitly/', include(urls))]

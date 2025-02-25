from django.conf.urls import url, include

from . import views

urls = [
    url(
        r'^videos/categories/',
        views.CategoriesView.as_view(),
        name='event-video-categories'
    ),
    url(
        r'^videos/',
        views.VideosView.as_view(),
        name='event-videos'
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/', include(urls)),
]

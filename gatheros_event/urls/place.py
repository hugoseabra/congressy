""" Urls de `Place` """
from django.conf.urls import include, url

from gatheros_event import views

urls = [
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.PlaceDeleteView.as_view(),
        name='place-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/$',
        views.PlaceEditFormView.as_view(),
        name='place-edit'
    ),
    url(
        r'^add/$',
        views.PlaceAddFormView.as_view(),
        name='place-add'
    ),
    url(
        r'^$',
        views.PlaceListView.as_view(),
        name='place-list'
    ),
]

urlpatterns_place = [
    url(
        r'^organizations/(?P<organization_pk>[\d]+)/places/',
        include(urls)
    ),
]

from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views

url_form = [
    url(
        r'^config',
        views.EventFormView.as_view(),
        name='form-config'
    ),
]

url_lot = [
    url(
        r'^(?P<lot_pk>[\d]+)/delete/$',
        views.LotDeleteView.as_view(),
        name='lot-delete'
    ),
    url(
        r'^(?P<lot_pk>[\d]+)/edit/$',
        views.LotEditFormView.as_view(),
        name='lot-edit'
    ),
    url(
        r'^add/$',
        views.LotAddFormView.as_view(),
        name='lot-add'
    ),
    url(
        r'^$',
        views.LotListView.as_view(),
        name='lot-list'
    ),
    url(
        r'^',
        RedirectView.as_view(
            pattern_name='gatheros_event:event-list',
            permanent=False
        )
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/form/', include(url_form)),
    url(r'^events/(?P<event_pk>[\d]+)/lots/', include(url_lot)),
]

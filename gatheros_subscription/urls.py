from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views

url_lot = [
    url(
        r'^$',
        views.LotListView.as_view(),
        name='lot-list'
    ),
    url(
        r'^add/$',
        views.LotAddFormView.as_view(),
        name='lot-add'
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
    url(r'^events/(?P<pk>[\d]+)/lots/', include(url_lot)),
]

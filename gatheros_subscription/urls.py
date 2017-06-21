from django.conf.urls import include, url
from django.views.generic import RedirectView

from gatheros_subscription import views

url_form = [
    url(
        r'^(?P<field_pk>[\d]+)/delete/$',
        views.EventFormDeleteView.as_view(),
        name='field-delete'
    ),
    url(
        r'^(?P<field_pk>[\d]+)/$',
        views.EventFormFieldEditView.as_view(),
        name='field-edit'
    ),
    url(
        r'^add',
        views.EventFormFieldAddView.as_view(),
        name='field-add'
    ),
    url(
        r'^config',
        views.EventConfigFormView.as_view(),
        name='fields-config'
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
    url(r'^events/(?P<event_pk>[\d]+)/fields/', include(url_form)),
    url(r'^events/(?P<event_pk>[\d]+)/lots/', include(url_lot)),
]

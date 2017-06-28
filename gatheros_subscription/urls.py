from django.conf.urls import include, url
from django.views.generic import RedirectView

from gatheros_subscription import views

url_subscription = [
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/attendnace/$',
        views.SubscriptionAttendanceView.as_view(),
        name='subscription-attendance'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/delete/$',
        views.SubscriptionDeleteView.as_view(),
        name='subscription-delete'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/edit/$',
        views.SubscriptionEditFormView.as_view(),
        name='subscription-edit'
    ),
    url(
        r'^add/$',
        views.SubscriptionAddFormView.as_view(),
        name='subscription-add'
    ),
    url(
        r'^attendance/search/$',
        views.SubscriptionAttendanceSearchView.as_view(),
        name='subscription-attendance-search'
    ),
    url(
        r'^$',
        views.SubscriptionListView.as_view(),
        name='subscription-list'
    ),
]

url_field_option = [
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.FieldOptionDeleteView.as_view(),
        name='field-option-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.FieldOptionEditView.as_view(),
        name='field-option-edit'
    ),
    url(
        r'^add/$',
        views.FieldOptionAddView.as_view(),
        name='field-option-add'
    ),
]

url_field = [
    url(
        r'^(?P<field_pk>[\d]+)/options/$',
        views.FieldOptionsView.as_view(),
        name='field-options'
    ),
    url(
        r'^(?P<field_pk>[\d]+)/order/$',
        views.EventFormFieldReorderView.as_view(),
        name='field-order'
    ),
    url(
        r'^(?P<field_pk>[\d]+)/delete/$',
        views.EventFormFieldDeleteView.as_view(),
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
        r'^',
        views.EventConfigFormFieldView.as_view(),
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
    url(r'^fieldoptions/', include(url_field_option)),
    url(r'^events/(?P<event_pk>[\d]+)/fields/', include(url_field)),
    url(r'^events/(?P<event_pk>[\d]+)/lots/', include(url_lot)),
    url(
        r'^events/(?P<event_pk>[\d]+)/subscriptions/',
        include(url_subscription)
    ),
]

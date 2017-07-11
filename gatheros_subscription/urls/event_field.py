from django.conf.urls import include, url

from gatheros_subscription import views

# url_event_field_option = [
#     url(
#         r'^(?P<pk>[\d]+)/delete/$',
#         views.EventFieldOptionDeleteView.as_view(),
#         name='event-field-option-delete'
#     ),
#     url(
#         r'^(?P<pk>[\d]+)/edit/$',
#         views.EventFieldOptionEditView.as_view(),
#         name='event-field-option-edit'
#     ),
#     url(
#         r'^add/$',
#         views.EventFieldOptionAddView.as_view(),
#         name='event-field-option-add'
#     ),
# ]

url_fields = [
    url(
        r'^(?P<pk>[\d]+)/requirement/$',
        views.EventFormFieldManageRequirementView.as_view(),
        name='event-manage-requirement'
    ),
    url(
        r'^(?P<pk>[\d]+)/activation/$',
        views.EventFormFieldManageActivationView.as_view(),
        name='event-manage-activation'
    ),
    url(
        r'^(?P<pk>[\d]+)/order/$',
        views.EventFormFieldReorderView.as_view(),
        name='event-field-order'
    ),
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.EventFormFieldDeleteView.as_view(),
        name='event-field-delete'
    ),
    url(
        r'^add/$',
        views.FieldsAddView.as_view(),
        name='event-field-add'
    ),
    url(
        r'^',
        views.EventConfigFormFieldView.as_view(),
        name='event-fields-config'
    ),
]

urlpatterns_event = [
    url(r'^events/(?P<event_pk>[\d]+)/fields/?', include(url_fields))
]

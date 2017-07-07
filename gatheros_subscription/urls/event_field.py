# from django.conf.urls import url
#
# from gatheros_subscription import views
#
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
#
#
#
# url_event_field = [
#     url(
#         r'^(?P<field_pk>[\d]+)/options/$',
#         views.EventFieldOptionsView.as_view(),
#         name='event-field-options'
#     ),
#     url(
#         r'^(?P<field_pk>[\d]+)/order/$',
#         views.EventFormFieldReorderView.as_view(),
#         name='event-field-order'
#     ),
#     url(
#         r'^(?P<field_pk>[\d]+)/delete/$',
#         views.EventFormFieldDeleteView.as_view(),
#         name='event-field-delete'
#     ),
#     url(
#         r'^(?P<field_pk>[\d]+)/$',
#         views.EventFormFieldEditView.as_view(),
#         name='event-field-edit'
#     ),
#     url(
#         r'^add',
#         views.EventFormFieldAddView.as_view(),
#         name='event-field-add'
#     ),
#     url(
#         r'^',
#         views.EventConfigFormFieldView.as_view(),
#         name='event-fields-config'
#     ),
# ]

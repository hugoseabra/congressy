from django.conf.urls import include, url

from gatheros_subscription import views

urls = [
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.FieldOptionDeleteView.as_view(),
        name='organization-field-option-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.FieldOptionEditView.as_view(),
        name='organization-field-option-edit'
    ),
    url(
        r'^add/$',
        views.FieldOptionAddView.as_view(),
        name='organization-field-option-add'
    ),
]

urlpatterns_field_option = [url(r'^fieldoptions/', include(urls))]

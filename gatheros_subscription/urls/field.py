from django.conf.urls import include, url

from gatheros_subscription import views

urls_organization_fields = [
    url(
        r'^add/$',
        views.FieldsAddView.as_view(),
        name='field-add'
    ),
    url(
        r'^',
        views.FieldsListView.as_view(),
        name='fields'
    ),
]

url_fields = [
    url(
        r'^(?P<field_pk>[\d]+)/options/$',
        views.FieldOptionsView.as_view(),
        name='field-options'
    ),
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.FieldsDeleteView.as_view(),
        name='field-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.FieldsEditView.as_view(),
        name='field-edit'
    ),

]

urlpatterns_field = [
    url(
        r'^organizations/(?P<organization_pk>[\d]+)/fields/',
        include(urls_organization_fields)
    ),
    url(
        r'^fields/',
        include(url_fields)
    ),
]

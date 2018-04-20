from django.conf.urls import include, url

from gatheros_subscription import views

urls = [
    url(
        r'^(?P<category_pk>[\d]+)/delete/$',
        views.LotDeleteView.as_view(),
        name='category-delete'
    ),
    url(
        r'^(?P<category_pk>[\d]+)/edit/$',
        views.LotEditFormView.as_view(),
        name='category-edit'
    ),
    url(
        r'^add/$',
        views.LotAddFormView.as_view(),
        name='category-add'
    ),
    url(
        r'^$',
        views.LotCategoryListView.as_view(),
        name='category-list'
    ),
]

urlpatterns_category = [
    url(r'^events/(?P<event_pk>[\d]+)/categories/', include(urls))
]

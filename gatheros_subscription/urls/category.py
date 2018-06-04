from django.conf.urls import include, url

from gatheros_subscription import views

urls = [
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.LotCategoryDeleteView.as_view(),
        name='category-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.LotCategoryEditView.as_view(),
        name='category-edit'
    ),
    url(
        r'^add/$',
        views.LotCategoryAddView.as_view(),
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

""" Urls dos opcionais """

from django.conf.urls import include, url
from django.views.generic import RedirectView

from addon import views


theme_urls = [
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.ThemeDeleteView.as_view(),
        name='theme-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.ThemeEditView.as_view(),
        name='theme-edit'
    ),
    url(
        r'^add/$',
        views.ThemeAddView.as_view(),
        name='theme-add'
    ),
    url(
        r'^$',
        views.ThemeListView.as_view(),
        name='theme-list'
    ),
]

optional_urls = [
    url(
        r'^products/(?P<optional_pk>[\d]+)/delete/$',
        views.OptionalProductDeleteView.as_view(),
        name='optional-product-delete'
    ),
    url(
        r'^products/(?P<optional_pk>[\d]+)/edit/$',
        views.OptionalProductEditView.as_view(),
        name='optional-product-edit'
    ),
    url(
        r'^services/(?P<optional_pk>[\d]+)/delete/$',
        views.OptionalServiceDeleteView.as_view(),
        name='optional-service-delete'
    ),
    url(
        r'^services/(?P<optional_pk>[\d]+)/edit/$',
        views.OptionalServiceEditView.as_view(),
        name='optional-service-edit'
    ),
    url(
        r'^products/$',
        views.OptionalProductListView.as_view(),
        name='optional-product-list'
    ),
    url(
        r'^services/$',
        views.OptionalServiceListView.as_view(),
        name='optional-service-list'
    ),
    url(
        r'^services/add/$',
        views.OptionalAddServiceView.as_view(),
        name='optional-service-add'
    ),
    url(
        r'^add/$',
        views.OptionalAddView.as_view(),
        name='optional-add'
    ),
    url(
        r'^$',
        RedirectView.as_view(
            pattern_name='addon:optional-service-list',
            permanent=False
        )
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/addons/', include(optional_urls)),
    url(r'^events/(?P<event_pk>[\d]+)/addons/themes/', include(
        theme_urls
    )),
]

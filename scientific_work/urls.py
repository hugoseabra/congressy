from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=True)
router.register(r'authors', views.AuthorViewSet)
router.register(r'works', views.WorkViewSet)
router.register(r'area_categories', views.AreaCategoryViewSet)

subscription_urls = [
    url(r'^add/$', views.WorkAddView.as_view(), name='work-add'),
    url(r'^config-list/$', views.WorkConfigListView.as_view(),
        name='work-config-list'),
    url(r'^(?P<pk>[\d]+)/authors$', views.AuthorPartialListView.as_view(),
        name='work-author-partial-list'),
]

event_urls = [
    url(r'^list/$', views.WorkListView.as_view(), name='work-list'),
    url(r'^area-categories-config/$', views.AreaCategoryConfigView.as_view(),
        name='scientific_event_config'),
]

api_urls = [
    url(r'^', include(router.urls)),
]

urlpatterns = [
    url(r'^api/scientific_work/', include(api_urls)),
    url(r'^subscription/(?P<subscription_pk>[0-9A-Fa-f-]+)/scientific_work/',
        include(subscription_urls)),
    url(r'^events/(?P<pk>[\d]+)/scientific_work/', include(event_urls)),
]

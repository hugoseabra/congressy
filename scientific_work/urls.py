from django.conf.urls import url, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter(trailing_slash=True)
router.register(r'authors', views.AuthorViewSet)
router.register(r'works', views.WorkViewSet)

urls = [
    url(r'^add/$', views.WorkAddView.as_view(), name='work-add'),
    url(r'^list/$', views.WorkListView.as_view(), name='work-list'),
    url(r'^(?P<pk>[\d]+)/authors$', views.AuthorPartialListView.as_view(),
        name='work-author-partial-list'),
]

api_urls = [
    url(r'^', include(router.urls)),
]

urlpatterns = [
    url(r'^subscription/(?P<subscription_pk>[0-9A-Fa-f-]+)/scientific_work/',
        include(urls)),
    url(r'^api/scientific_work/', include(api_urls)),

]

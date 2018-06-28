""" gatheros_subscription urls """
# pylint: skip-file
from django.conf.urls import include, url
from rest_framework import routers

from gatheros_subscription import viewsets, views

router = routers.DefaultRouter()
router.register(r'lots', viewsets.LotViewSet)

urls = [
    url(
        r'^(?P<lot_pk>[\d]+)/survey/(?P<survey_pk>[\d]+)$',
        views.LotChangeSurveyAPIView.as_view(),
        name='lot-change-survey-api'
    ),
    url(
        r'^(?P<lot_pk>[\d]+)/survey/$',
        views.LotChangeSurveyAPIView.as_view(),
        name='lot-change-survey-api'
    ),
]
single_endpoints = [url(r'^events/(?P<event_pk>[\d]+)/lots/', include(urls))]

urlpatterns = router.urls
urlpatterns += single_endpoints

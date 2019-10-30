""" gatheros_subscription urls """
# pylint: skip-file
from django.conf.urls import include, url
from rest_framework import routers

from gatheros_subscription import viewsets, views

router = routers.DefaultRouter()
router.register('subscription/lots', viewsets.LotViewSet)
router.register('subscription/subscriptions/billing',
                viewsets.SubscriptionBillingViewSet)
router.register('subscription/subscriptions', viewsets.SubscriptionViewSet)
router.register('survey/surveys', viewsets.EventSurveyViewSet)
router.register('survey/questions', viewsets.QuestionViewSet)

# router.register(
#     'subscription/surveys/{survey_pk}/questions',
#     viewsets.QuestionViewSet
# )

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

subs_urls = [
    url('^list/$',
        viewsets.SubscriptionListViewSet.as_view(),
        name='subscription-list-api'),
]

survey_urls = [
    url(
        r'^survey/surveys/(?P<survey_pk>[\d]+)/questions',
        viewsets.QuestionViewSet.as_view({'get': 'list'}),
        name='survey'
    ),
]

single_endpoints = [url(r'^events/(?P<event_pk>[\d]+)/lots/', include(urls))]
sub_single_endpoints = [
    url(r'^events/(?P<event_pk>[\d]+)/subsriptions/', include(subs_urls)),
    url(r'^events/(?P<event_pk>[\d]+)/subscriptions/export/',
        viewsets.SubscriptionExporterViewSet.as_view())
]

urlpatterns = router.urls
urlpatterns += single_endpoints
urlpatterns += sub_single_endpoints
urlpatterns += survey_urls

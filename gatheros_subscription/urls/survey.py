""" Survey URL's  """
from django.conf.urls import include, url

from gatheros_subscription import views

urls = [
    url(
        r'^(?P<survey_pk>[\d]+)/edit$',
        views.SurveyEditView.as_view(),
        name='survey-edit'
    ),
    url(
        r'^(?P<pk>[\d]+)/delete$',
        views.SurveyDeleteView.as_view(),
        name='survey-delete'
    ),
    url(
        r'^$',
        views.SurveyListView.as_view(),
        name='survey-list'
    ),
]

urlpatterns_survey = [
    url(r'^events/(?P<event_pk>[\d]+)/survey/', include(urls)),
]


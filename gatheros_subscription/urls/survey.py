""" Survey URL's  """
from django.conf.urls import include, url

from gatheros_subscription import views

urls = [
    url(
        r'^create$',
        views.EventSurveyCreateView.as_view(),
        name='survey-create'
    ),
    url(
        r'^(?P<survey_pk>[\d]+)/edit$',
        views.SurveyEditView.as_view(),
        name='survey-edit'
    ),
    url(
        r'^delete$',
        views.EventSurveyDeleteAjaxView.as_view(),
        name='survey-ajax-delete'
    ),
    url(
        r'^event-survey/edit$',
        views.EventSurveyEditAjaxView.as_view(),
        name='survey-ajax-edit'
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

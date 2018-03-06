""" Survey URL's  """
from django.conf.urls import include, url

from . import views

urls = [
    url(
        r'^',
        views.CreateSurveyView.as_view(),
        name='survey-create'
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/survey/', include(urls)),
]


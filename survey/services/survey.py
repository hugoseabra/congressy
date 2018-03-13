"""
Application Service
"""
from survey.services import mixins
from survey.managers import SurveyManager


class SurveyService(mixins.ApplicationServiceMixin):
    """ Application Service """
    manager_class = SurveyManager

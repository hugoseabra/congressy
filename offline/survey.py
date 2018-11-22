from .base import Base, FilterMixin


class SurveyOffline(Base, FilterMixin):
    filter_dict = {
        'survey.Option': 'question__survey__event__event_id',
        'survey.Question': 'survey__event__event_id',
        'survey.Answer': 'question__survey__event__event_id',
    }

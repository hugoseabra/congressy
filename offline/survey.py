from .base import Base, FilterMixin


class SurveyOffline(Base, FilterMixin):
    filter_dict = {
        'survey.Question': 'survey__event__event_id',
    }

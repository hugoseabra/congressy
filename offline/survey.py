from .base import Base, FilterMixin


class SurveyOffline(Base, FilterMixin):
    filter_dict = {
        'survey.Survey': 'event__event_id',
    }

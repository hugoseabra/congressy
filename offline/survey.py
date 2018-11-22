from .base import OfflineBase, FilterMixin


class SurveyOffline(OfflineBase, FilterMixin):
    filter_dict = {
        'survey.Survey': 'event__event_id',
        'survey.Question': 'survey__event__event_id',
        'survey.Option': 'question__survey__event__event_id',
        'survey.Answer': 'question__survey__event__event_id',
        'survey.Author': 'survey__event__event_id',
    }

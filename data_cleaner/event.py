from .base import DataCleanerBase, EraserMixin, FilterMixin


class EventDataCleaner(DataCleanerBase, EraserMixin, FilterMixin):
    erase_list = [
        'gatheros_event.Invitation',
    ]

    filter_dict = (
        ('gatheros_event.Event', 'pk',),
        ('gatheros_event.Organization', 'events',),
        ('gatheros_event.Member', 'organization__events',),
        ('gatheros_event.Place', 'event_id',),
        ('gatheros_event.Info', 'event_id',),
        ('gatheros_event.FeatureConfiguration', 'event_id',),
        ('gatheros_event.FeatureManagement', 'event_id',),
    )

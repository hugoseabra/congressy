from .base import DataCleanerBase, EraserMixin


class DjangoCronDataCleaner(DataCleanerBase, EraserMixin):
    erase_list = [
        'django_cron.CronJobLog',
    ]

from .base import OfflineBase, EraserMixin


class DjangoCronOffline(OfflineBase, EraserMixin):
    erase_list = [
        'django_cron.CronJobLog',
    ]

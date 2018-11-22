from .base import Base, EraserMixin


class DjangoCronOffline(Base, EraserMixin):
    erase_list = [
        'django_cron.CronJobLog',
    ]

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CgsyVideoConfig(AppConfig):
    name = 'cgsy_video'
    verbose_name = _('Congressy Videos')

    # noinspection PyUnresolvedReferences
    def ready(self):
        import cgsy_video.signals

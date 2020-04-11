""" Signals """
from django.db.models.signals import post_save
from django.dispatch import receiver

from cgsy_video import workers
from gatheros_event.models import Event


@receiver(post_save, sender=Event)
def synchronize_video_config(instance: Event, raw, **_):
    """ Atualiza configuração de vídeo na integração """
    if raw is True:
        return

    if instance.feature_management.videos is False:
        return

    if hasattr(instance, 'video_config') is False:
        workers.create_video_config.delay(instance.pk)
        return

    workers.sync_event_user.delay(instance.pk)
    workers.sync_namespace.delay(instance.pk)
    workers.sync_project.delay(instance.pk)

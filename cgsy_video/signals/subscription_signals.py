""" Signals """
from django.db.models.signals import post_save
from django.dispatch import receiver

from cgsy_video import workers
from gatheros_subscription.models import Subscription


@receiver(post_save, sender=Subscription)
def synchronize_subscription(instance: Subscription, raw, **_):
    """ Atualiza configuração de vídeo na integração """
    if raw is True:
        return

    event = instance.event

    if event.feature_management.videos is False:
        return

    if hasattr(event, 'video_config') is False:
        workers.create_video_config.delay(event.pk)

    workers.sync_subscriber.delay(instance.pk)

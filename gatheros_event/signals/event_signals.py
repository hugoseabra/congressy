from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_event.models import Event, ConfFeatureRelease
from mailer.services import notify_new_event


@receiver(post_save, sender=Event)
def create_conf_feature_release(instance, raw, created, **_):
    if raw is True:
        return

    if created is True:
        try:
            instance.feature_relase
        except AttributeError:
            ConfFeatureRelease.objects.create(event=instance)


@receiver(post_save, sender=Event)
def send_email_on_new_event(instance, raw, created, **_):
    if raw is True:
        return

    if created and settings.DEBUG is False:
        notify_new_event(instance)

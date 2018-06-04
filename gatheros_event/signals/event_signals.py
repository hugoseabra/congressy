from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from gatheros_event.models import Event
from mailer.services import notify_new_event


@receiver(post_save, sender=Event)
def send_email_on_new_event(instance, raw, created, **_):

    if raw is True:
        return

    if created and settings.DEBUG is False:
        notify_new_event(instance)

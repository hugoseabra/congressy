from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_event.models import Info
from gatheros_event.signals.helpers import update_event_publishing


@receiver(post_save, sender=Info)
def update_event_publishing_state(instance, **_):
    """ Altera as flags de publicado quando evento muda de tipo """

    event = instance.event
    update_event_publishing(event)

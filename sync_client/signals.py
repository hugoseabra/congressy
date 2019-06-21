""" Signals do model `sync_client` """
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save
from django.db.transaction import atomic
from django.dispatch import receiver

from gatheros_event.models import Person
from sync_client.models import SyncItem


@receiver(pre_save, sender=Person)
def save_sync_item(instance, raw, using, updated_fields):
    """ Altera as flags de fatures quando um evento muda de tipo """

    content_type = ContentType.objects.get_for_model(instance)
    key_tupple = content_type.natural_key()

    object_type = "{}.{}".format(key_tupple[0], key_tupple[1])
    object_id = instance.pk

    with atomic():
        try:
            item = SyncItem.objects.get(object_type=object_type,
                                        object_id=object_id)

        except SyncItem.DoesNotExist:
            item = SyncItem(
                object_type=object_type,
                object_id=object_id,
            )

        item.object_repr = str(instance)
        item.change_messages = updated_fields

    object_repr = str(instance)


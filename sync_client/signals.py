""" Signals do model `sync_client` """
import json
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.db.transaction import atomic
from django.dispatch import receiver

from attendance.models import AttendanceService, Checkin, Checkout
from gatheros_event.models import Person
from gatheros_subscription.models import Subscription
from payment.models import Transaction, TransactionStatus
from sync_client.models import SyncItem

from django.core import serializers


@receiver(post_save, sender=Person)
@receiver(post_save, sender=Subscription)
@receiver(post_save, sender=Transaction)
@receiver(post_save, sender=TransactionStatus)
@receiver(post_save, sender=AttendanceService)
@receiver(post_save, sender=Checkin)
@receiver(post_save, sender=Checkout)
def save_sync_item_for_creation_edition(instance, raw, **_):
    if raw is True:
        return

    force_sync = \
        hasattr(instance, 'sync_force') and instance.sync_force is True

    process_type = SyncItem.CREATION if instance.is_new() else SyncItem.EDITION

    updated_fields = instance.whats_changed()

    if force_sync is False \
            and process_type == SyncItem.EDITION \
            and not updated_fields:
        return

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

        item.process_type = process_type
        item.object_repr = str(instance)
        item.process_time = datetime.now()
        data = json.loads(serializers.serialize("json", [instance]))
        item.content = json.dumps(data[0])

        item.save()


@receiver(post_delete, sender=Person)
@receiver(post_delete, sender=Subscription)
@receiver(post_delete, sender=Transaction)
@receiver(post_delete, sender=TransactionStatus)
@receiver(post_delete, sender=AttendanceService)
@receiver(post_delete, sender=Checkin)
@receiver(post_delete, sender=Checkout)
def save_sync_item_for_deletion(instance, **_):
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

        item.process_type = SyncItem.DELETION
        item.object_repr = str(instance)
        item.content = None
        item.process_time = datetime.now()

        item.save()

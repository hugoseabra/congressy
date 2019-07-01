""" Signals do model `sync_client` """
import json
from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete, pre_save
from django.db.transaction import atomic
from django.dispatch import receiver

from addon.models import Theme, Service, Product, SubscriptionService, \
    SubscriptionProduct
from attendance.models import AttendanceService, Checkin, Checkout
from gatheros_event.models import Person
from gatheros_subscription.models import Subscription, EventSurvey, \
    LotCategory, Lot
from payment.models import Transaction, TransactionStatus
from survey.models import Survey, Question, Option, Answer, Author
from sync_client.models import SyncItem

from django.core import serializers


@receiver(post_save, sender=User)
def save_sync_item_for_user(instance, raw, **_):
    if raw is True:
        return

    process_type = SyncItem.CREATION \
        if instance._state.adding is True else SyncItem.EDITION

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


@receiver(post_save, sender=LotCategory)
@receiver(post_save, sender=Lot)
@receiver(post_save, sender=Person)
@receiver(post_save, sender=Subscription)
@receiver(post_save, sender=Transaction)
@receiver(post_save, sender=TransactionStatus)
@receiver(post_save, sender=AttendanceService)
@receiver(post_save, sender=Checkin)
@receiver(post_save, sender=Checkout)
@receiver(post_save, sender=EventSurvey)
@receiver(post_save, sender=Survey)
@receiver(post_save, sender=Question)
@receiver(post_save, sender=Option)
@receiver(post_save, sender=Answer)
@receiver(post_save, sender=Author)
@receiver(post_save, sender=Theme)
@receiver(post_save, sender=Service)
@receiver(post_save, sender=Product)
@receiver(post_save, sender=SubscriptionService)
@receiver(post_save, sender=SubscriptionProduct)
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
        item.object_repr = str(instance).strip()
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
@receiver(post_delete, sender=Answer)
@receiver(post_delete, sender=Author)
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

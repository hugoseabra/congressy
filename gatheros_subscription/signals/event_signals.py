from datetime import datetime, timedelta

from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_event.models import Event
from gatheros_subscription.models import Lot


@receiver(post_save, sender=Event)
def manage_related_lot_when_subscription_enabled(sender, instance, created, raw, **_):
    # Disable when loaded by fixtures
    if raw is True:
        return

    # Process only if subscription_type is changed
    if created is False and instance.has_changed('subscription_type') is False:
        return

    if instance.subscription_type not in [sender.SUBSCRIPTION_SIMPLE, sender.SUBSCRIPTION_BY_LOTS]:
        _remove_lots(event=instance)
        return

    num_lots = Lot.objects.filter(event=instance).count()

    if instance.subscription_type == sender.SUBSCRIPTION_SIMPLE:
        if num_lots > 0:
            _merge_lots_and_subscriptions(event=instance)
            return

        _create_internal_lot(event=instance)

    elif instance.subscription_type == sender.SUBSCRIPTION_BY_LOTS:
        if num_lots > 0:
            _convert_internal_lot_to_external(event=instance)
            return

        _create_external_lot(event=instance)


def _remove_lots(event):
    for lot in event.lots.all():
        if lot.subscriptions.count() > 0:
            raise Exception('Você já possui inscrições. Exclua os lotes primeiro para depois desativar as inscrições.')

    event.lots.all().delete()


def _get_lot_date_start(event):
    if event.date_start > datetime.now():
        return event.date_start

    return event.date_start - timedelta(days=1)


def _create_internal_lot(event):
    Lot.objects.create(
        name=Lot.INTERNAL_DEFAULT_NAME,
        event=event,
        date_start=_get_lot_date_start(event),
        internal=True
    )


def _create_external_lot(event):
    Lot.objects.create(
        name='Lote 1',
        event=event,
        date_start=_get_lot_date_start(event),
        internal=False
    )


def _merge_lots_and_subscriptions(event):
    """
    1. check if lot(s) has(have) subscription(s)
    2. find the most recent lot
    3. transfer subscription(s) to most recent lot
    4. convert most recent lot to internal
    5. remove other lots
    """
    lots = event.lots.all().order_by('-pk')

    if lots.count() == 0:
        return

    most_recent_lot = lots[0]

    subscriptions = []
    for lot in lots[1:]:
        subs = lot.subscriptions.all()
        if not subs:
            continue

        subscriptions += subs

    for lot in lots[1:]:
        lot.delete()

    # normalize
    _merge_subscriptions(most_recent_lot, subscriptions)

    most_recent_lot.name = Lot.INTERNAL_DEFAULT_NAME
    most_recent_lot.internal = True
    most_recent_lot.price = None
    most_recent_lot.save()


def _merge_subscriptions(lot, subscriptions):
    # normalize
    subscription_counter = 0
    for sub in subscriptions:
        if subscription_counter == 0:
            count_max = lot.subscriptions.aggregate(Max('count'))
            subscription_counter = count_max['count__max']

        sub.lot = lot
        sub.count = subscription_counter + 1
        sub.save()

        if subscription_counter > 0:
            subscription_counter += 1


def _convert_internal_lot_to_external(event):
    lots = event.lots.all().order_by('pk')

    if lots.count() == 0:
        return

    counter = lots.count()
    for lot in lots:
        if lot.name == Lot.INTERNAL_DEFAULT_NAME:
            lot.name = 'Lote ' + str(counter)

        if event.date_start < lot.date_end:
            lot.date_start = _get_lot_date_start(event)

        lot.internal = False
        lot.save()

        counter += 1

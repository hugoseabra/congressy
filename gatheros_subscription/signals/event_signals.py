from django.db.models import Max
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from gatheros_event.models import Event
from gatheros_subscription.models import Lot


@receiver(pre_save, sender=Event)
def clean_related_lots_when_subscription_disabled(instance, raw, **_):
    # Disable when loaded by fixtures
    if raw is True:
        return

    if instance.subscription_type == Event.SUBSCRIPTION_DISABLED:
        _remove_lots(event=instance)
        return


@receiver(post_save, sender=Event)
def manage_related_lot_when_subscription_enabled(instance, created, raw, **_):
    # Disable when loaded by fixtures
    if raw is True:
        return

    # Process only if, in edition, subscription_type is changed
    if created is False and instance.has_changed('subscription_type') is False:
        return

    num_lots = Lot.objects.filter(event=instance).count()

    if instance.subscription_type == Event.SUBSCRIPTION_SIMPLE:
        if num_lots > 0:
            _merge_lots_and_subscriptions(event=instance)
            return

        _create_internal_lot(event=instance)

    elif instance.subscription_type == Event.SUBSCRIPTION_BY_LOTS:
        if num_lots > 0:
            _convert_internal_lot_to_external(event=instance)
            return

        _create_external_lot(event=instance)


def _remove_lots(event):
    for lot in event.lots.all():
        if lot.subscriptions.count() > 0:
            raise Exception(
                'Lote já possui inscrições. Não é possível desativar as'
                ' inscrições.'
            )

    event.lots.all().delete()


def _create_internal_lot(event):
    lot = Lot(
        name=Lot.INTERNAL_DEFAULT_NAME,
        event=event,
        internal=True
    )
    lot.adjust_unique_lot_date()
    lot.save()


def _create_external_lot(event):
    lot = Lot(
        name='Lote 1',
        event=event,
        internal=False
    )
    lot.adjust_unique_lot_date(force=True)
    lot.save()


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
    most_recent_lot.limit = 0

    subscriptions = []
    for lot in lots[1:]:
        if lot.limit:
            most_recent_lot.limit += lot.limit

        subs = lot.subscriptions.all()
        if not subs:
            continue

        subscriptions += subs

    # normalize
    _merge_subscriptions(most_recent_lot, subscriptions)

    for lot in lots[1:]:
        lot.delete()

    most_recent_lot.name = Lot.INTERNAL_DEFAULT_NAME
    most_recent_lot.internal = True
    most_recent_lot.price = None

    most_recent_lot.adjust_unique_lot_date()
    most_recent_lot.save()


def _merge_subscriptions(lot, subscriptions):
    """
    Normaliza as inscrições no lote.
    :param lot: Lote a receber inscrições
    :param subscriptions: Collection de inscrições
    :return: None
    """
    has_subscriptions = lot.subscriptions.count() > 0
    subscription_counter = 0
    for sub in subscriptions:
        if subscription_counter == 0:
            if has_subscriptions:
                count_max = lot.subscriptions.aggregate(Max('count'))
                subscription_counter = count_max.get('count__max', 0)
            else:
                subscription_counter = 0

        sub.lot = lot
        sub.count = subscription_counter + 1
        sub.save()

        if subscription_counter > 0:
            subscription_counter += 1


def _convert_internal_lot_to_external(event):
    lots = event.lots.all().order_by('pk')

    if lots.count() == 0:
        return

    lot = event.lots.first()
    lot.name = 'Lote 1'
    lot.internal = False

    lot.adjust_unique_lot_date()
    lot.save()

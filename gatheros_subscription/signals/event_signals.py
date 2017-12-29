""" Signals do model `Event`. """
import os

from django.db.models import Max
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from gatheros_event.models import Event
from gatheros_subscription.models import Lot, Form


@receiver(post_save, sender=Event)
def create_form(instance, raw, **_):
    # Disable when loaded by fixtures
    if raw is True:
        return

    if instance.subscription_type != Event.SUBSCRIPTION_DISABLED:
        try:
            instance.form
        except Form.DoesNotExist:
            Form.objects.create(event=instance)


@receiver(post_delete, sender=Event)
def clear_files_on_delete(instance, **_):
    """ Apaga arquivos relacionados quando Evento é apagado """

    path = None

    def _delete_media(field):
        """ Lógica de remoção de arquivos """
        nonlocal path
        if bool(field) and os.path.isfile(field.path):
            path = os.path.dirname(field.path)
            field.delete(False)

    # Chamando remoção de arquivos
    _delete_media(instance.banner_slide)
    _delete_media(instance.banner_small)
    _delete_media(instance.banner_top)

    # Remove diretório se estiver vazio
    if path and not os.listdir(path):
        os.rmdir(path)


@receiver(pre_save, sender=Event)
def clean_related_lots_when_subscription_disabled(instance, raw, **_):
    """ Limpa lotes existente quando inscrição passa a ser desativada. """

    # Disable when loaded by fixtures
    if raw is True:
        return

    if instance.subscription_type == Event.SUBSCRIPTION_DISABLED:
        _remove_lots(event=instance)
        return


@receiver(post_save, sender=Event)
def manage_related_lot_when_subscription_enabled(instance, created, raw, **_):
    """ Gerencia lotes relacionados quando inscrições são ativadas. """
    # Disable when loaded by fixtures
    if raw is True:
        return

    # Process only if, in edition, subscription_type is changed
    if created is False and instance.has_changed('subscription_type') is False:
        return

    num_lots = Lot.objects.filter(event=instance).count()

    # Em inscrições simple
    if instance.subscription_type == Event.SUBSCRIPTION_SIMPLE:
        # Se lotes, uni-los.
        if num_lots > 0:
            _merge_lots_and_subscriptions(event=instance)
            return

        # Cria lote interno.
        _create_internal_lot(event=instance)

    # Inscrições gerenciados por lote
    elif instance.subscription_type == Event.SUBSCRIPTION_BY_LOTS:
        # Se lotes, convertê-los para externos
        if num_lots > 0:
            _convert_internal_lot_to_external(event=instance)
            return

        # Cria lote externo
        _create_external_lot(event=instance)


def _remove_lots(event):
    """ Remove lotes sem inscrições do evento. """
    lots_with_subs = []

    for lot in event.lots.all():
        if lot.subscriptions.count() > 0:
            lots_with_subs.append('{} (#{})'.format(lot.name, lot.pk))
            continue

        lot.delete()

    if lots_with_subs:
        raise Exception(
            'Há lotes que ainda possuem inscrições: {}. Não é possível'
            ' desativar as inscrições.'.format(', '.join(lots_with_subs))
        )


def _create_internal_lot(event):
    """ Cria lote interno para evento. """
    lot = Lot(
        name=Lot.INTERNAL_DEFAULT_NAME,
        event=event,
        internal=True
    )
    lot.adjust_unique_lot_date()
    lot.save()


def _create_external_lot(event):
    """ Cria lote externo para evento. """
    lot = Lot(
        name='Lote 1',
        event=event,
        internal=False
    )
    lot.adjust_unique_lot_date(force=True)
    lot.save()


def _merge_lots_and_subscriptions(event):
    """
    Junta lotes existentes cumprindo os seguintes passos:
        1. verifica se lote(s) possui(em) inscrições(s)
        2. encontra o lote mais recente
        3. transfere inscrição(ões) para o lote mais recente
        4. converte lote mais recente para interno
        5. remove outros lots

    :param event: Evento
    :return: None
    """
    lots = event.lots.all().order_by('-pk')

    if lots.count() == 0:
        return

    most_recent_lot = lots[0]

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

    # Nome padrão
    most_recent_lot.name = Lot.INTERNAL_DEFAULT_NAME

    # Torna-o ilimitado.
    most_recent_lot.limit = 0

    # Torna-lo gratuito
    most_recent_lot.price = None

    most_recent_lot.internal = True

    # Ajusta data dentro dos limites do evento.
    most_recent_lot.adjust_unique_lot_date()
    most_recent_lot.save()


def _merge_subscriptions(lot, subscriptions):
    """
    Uni inscrições de diversos lotes em um só.

    :param lot: Lote a receber inscrições
    :param subscriptions: Lista de inscrições
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
    """ Converte lotes internos para externos. """
    lots = event.lots.all().order_by('pk')

    if lots.count() == 0:
        return

    lot = event.lots.first()
    lot.name = 'Lote 1'
    lot.internal = False

    lot.adjust_unique_lot_date()
    lot.save()

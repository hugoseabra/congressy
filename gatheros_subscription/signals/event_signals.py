""" Signals do model `Event`. """
import os
from datetime import datetime

from django.db.models.signals import post_delete, post_save
from django.db.transaction import atomic
from django.dispatch import receiver

from gatheros_event.models import Event
from ticket.models import Ticket, Lot


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
    if path is not None and not os.listdir(path):
        os.rmdir(path)


@receiver(post_save, sender=Event)
def create_default_ticket(instance, created, raw, **_):
    """ Gerencia lotes relacionados quando inscrições são ativadas. """
    # Disable when loaded by fixtures
    if raw is True or created is False:
        return

    with atomic():
        ticket = Ticket.objects.create(
            event_id=instance.pk,
            name='Geral',
            active=True,
        )

        Lot.objects.create(
            ticket_id=ticket.pk,
            date_start=datetime.now(),
            date_end=instance.date_end,
        )

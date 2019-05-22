from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_subscription.models import Subscription


@receiver(post_save, sender=Subscription)
def update_num_subs_flag(instance, raw, **_):
    if raw is True:
        return

    lot = instance.ticket_lot
    ticket = lot.ticket

    # Atualização de número de inscrições em um lote
    lot.update_lot_num_subs()

    # Atualização de número de inscrições no ingresso
    ticket.update_audience_category_num_subs()

    # # Ajustes de datas de lotes para virada automática em caso de lote lotado
    # if lot.is_full:
    #     ticket.anticipate_lots()
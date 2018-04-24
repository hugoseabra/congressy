from django.db.models.signals import post_save, post_delete

from addon.models import ServicePrice, ProductPrice


def activate_optional_cost_flag(instance, raw, created, **_):
    """
        Atualiza has_cost do Optional para True quando um novo preço é
        adicionado.
    """

    # Fixture or not new entity
    if raw is True or created is False:
        return

    if hasattr(instance, 'optional_service'):
        optional = instance.optional_service
    else:
        optional = instance.optional_product

    optional.has_cost = True
    optional.save()


def deactivate_optional_cost_flag(instance, **_):
    """
        Atualiza has_cost do Optional para False quando um preço é excluído
        e não há outros preços vinculados.
    """
    if hasattr(instance, 'optional_service'):
        optional = instance.optional_service
    else:
        optional = instance.optional_product

    prices = optional.prices.count()

    if prices == 0:
        optional.has_cost = False
        optional.save()


post_save.connect(activate_optional_cost_flag, sender=ProductPrice)
post_save.connect(activate_optional_cost_flag, sender=ServicePrice)

post_delete.connect(deactivate_optional_cost_flag, sender=ProductPrice)
post_delete.connect(deactivate_optional_cost_flag, sender=ServicePrice)

"""
gatheros_event templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def event_payment_type(event):
    paied = False
    free = False

    for lot in event.lots.all():
        if lot.price and lot.price > 0:
            paied = True

        if not lot.price:
            free = True

    if paied and free:
        return 'mixed'

    if not free and paied:
        return 'paied'

    return 'free'


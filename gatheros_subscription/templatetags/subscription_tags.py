"""
gatheros_subscription templatetags
"""
import json
from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe

from gatheros_subscription.models import Subscription

register = template.Library()


@register.simple_tag
def jsonify(obj):
    if isinstance(obj, QuerySet):
        return serialize('json', obj)

    return mark_safe(json.dumps(obj, ensure_ascii=False))


@register.simple_tag
def is_list(value):
    """ Verifica se valor é uma lista. """
    return isinstance(value, list)


@register.simple_tag
def get_gatheros_field(form, form_field):
    """ Recupera `Field` pelo nome único no formulário. """
    return form.get_gatheros_field_by_name(form_field.name)


@register.simple_tag(takes_context=True)
def is_filter_selected(context, filter_name, value):
    """ Checks whether a given filter field is selected. """
    request = context['request']
    filter_values = request.GET.getlist(filter_name)

    if not filter_values:
        return {}

    # All request's querystring data comes as string
    return str(value) in filter_values


@register.simple_tag
def event_count_completed_subscriptions(event):
    return Subscription.objects.filter(
        lot__event=event,
        completed=True,
        test_subscription=False,

        status__in=[
            Subscription.CONFIRMED_STATUS,
            Subscription.AWAITING_STATUS
        ],
    ).count()


@register.simple_tag
def lot_count_completed_subscriptions(lot):
    return Subscription.objects.filter(
        lot=lot,
        completed=True,
        test_subscription=False,
        status__in=[
            Subscription.CONFIRMED_STATUS,
            Subscription.AWAITING_STATUS
        ],
    ).count()


@register.simple_tag
def is_subscription_free(subscription):
    if not subscription:
        return False

    has_products = subscription.subscription_products.filter(
        optional_price__gt=0
    ).count() > 0

    if has_products is True:
        return False

    has_services = subscription.subscription_services.filter(
        optional_price__gt=0
    ).count() > 0

    if has_services is True:
        return False

    is_free = subscription.free is True
    if is_free is False:
        return False

    return True

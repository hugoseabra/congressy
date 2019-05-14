"""
gatheros_event templatetags
"""
import math
from django import template

register = template.Library()


@register.simple_tag
def get_subscription_services(subscription):
    services = []

    qs = subscription.subscription_services
    qs = qs.filter(optional__lot_category_id=subscription.lot.category_id)

    for sub_serv in qs.order_by('optional__schedule_start'):
        services.append(sub_serv.optional)

    column1 = list()
    column2 = list()

    num_services = len(services)
    if num_services > 1:
        num_column1 = int(math.ceil(num_services / 2))
        chunk_column1 = list()

        for i in range(0, num_column1):
            column1.append(services[i])

        for i in range(num_column1, num_services):
            column2.append(services[i])

    else:
        column1 = services

    return (column1, column2);


@register.inclusion_tag('subscription/includes/addon_services_item.html')
def subscription_service_row(event, service):
    return {'service': service, 'event': event}

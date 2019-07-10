"""
gatheros_event templatetags
"""
import math
from django import template

register = template.Library()


@register.simple_tag
def get_subscription_products(subscription):
    products = []

    qs = subscription.subscription_products
    qs = qs.filter(optional__lot_category_id=subscription.lot.category_id)

    for sub_prod in qs.order_by('optional__name'):
        products.append(sub_prod.optional)

    column1 = list()
    column2 = list()

    num_products = len(products)
    if num_products > 1:
        num_column1 = int(math.ceil(num_products / 2))
        chunk_column1 = list()

        for i in range(0, num_column1):
            column1.append(products[i])

        for i in range(num_column1, num_products):
            column2.append(products[i])

    else:
        column1 = products

    return (column1, column2);


@register.inclusion_tag('subscription/includes/addon_products_item.html')
def subscription_product_row(event, product):
    return {'product': product, 'event': event}

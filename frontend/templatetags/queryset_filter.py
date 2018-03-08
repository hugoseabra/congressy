"""
gatheros_subscription templatetags
"""

from django import template
from ast import literal_eval

register = template.Library()


@register.filter()
def queryset_filter(queryset, args):
    return queryset.filter(args)


@register.filter()
def queryset_count(queryset, arg):
    kwargs = dict(
        (k, literal_eval(v))
        for k, v in (pair.split('=') for pair in arg.split())
    )
    return queryset.filter(**kwargs).count()

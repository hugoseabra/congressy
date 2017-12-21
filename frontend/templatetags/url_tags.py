"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """ Repõe o valor dos campos utilizando `urlencode()` """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

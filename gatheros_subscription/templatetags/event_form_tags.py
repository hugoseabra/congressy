"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def form_is_default(form, field_name):
    return form.is_default(field_name)

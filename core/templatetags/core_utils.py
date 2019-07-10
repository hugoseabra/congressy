"""
core templatetags
"""
import math
from django import template

register = template.Library()


@register.simple_tag
def get_from_dict(obj_dict, key):
    if key not in obj_dict:
        return None

    return obj_dict.get(key)

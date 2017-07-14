"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def is_list(value):
    """ Verifica se valor é uma lista. """
    return isinstance(value, list)


@register.simple_tag
def get_gatheros_field(form, form_field):
    """ Recupera `Field` pelo nome único no formulário. """
    return form.get_gatheros_field_by_name(form_field.name)

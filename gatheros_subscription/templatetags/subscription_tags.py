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


@register.simple_tag(takes_context=True)
def is_filter_selected(context, filter_name, value):
    """ Checks whether a given filter field is selected. """
    request = context['request']
    filter_values = request.GET.getlist(filter_name)

    print(value)

    if not filter_values:
        return {}

    # All request's querystring data comes as string
    return str(value) in filter_values

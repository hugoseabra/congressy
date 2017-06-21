"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def form_is_default(form, field_name):
    return form.is_default(field_name)


@register.simple_tag
def get_field_by_name(form, field_name):
    return form.get_field_by_name(field_name)


@register.simple_tag
def user_can_delete(user, form, field_name):
    field = get_field_by_name(form, field_name)
    not_default = form.is_default(field_name) is False
    can_delete = user.has_perm('gatheros_subscription.delete_field', field)

    return not_default and can_delete


@register.simple_tag
def user_can_edit(user, form, field_name):
    field = get_field_by_name(form, field_name)
    not_default = form.is_default(field_name) is False
    can_edit = user.has_perm('gatheros_subscription.change_field', field)

    return not_default and can_edit

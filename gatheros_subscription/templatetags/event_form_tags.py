"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def user_can_delete(user, field):
    not_default = field.form_default_field is False
    can_delete = user.has_perm('gatheros_subscription.delete_field', field)

    return not_default and can_delete


@register.simple_tag
def user_can_edit(user, field):
    not_default = field.form_default_field is False
    can_edit = user.has_perm('gatheros_subscription.change_field', field)

    return not_default and can_edit

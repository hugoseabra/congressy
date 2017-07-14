"""
gatheros_event templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def get_member_group_name(organization, user):
    """ Recupera nome do grupo em que o usuário está na organização. """
    member = organization.get_member(user)
    if not member:
        return '-'

    return member.get_group_display()


@register.simple_tag
def get_member_group(organization, user):
    """ Recupera alias do grupo em que o usuário está na organização. """
    member = organization.get_member(user)
    if not member:
        return '-'

    return member.group

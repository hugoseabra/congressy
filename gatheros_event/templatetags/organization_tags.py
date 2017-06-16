"""
gatheros_event templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def get_member_group_name(organization, user):
    member = organization.get_member(user)
    if not member:
        return '-'

    return member.get_group_display()


@register.simple_tag
def get_member_group(organization, user):
    member = organization.get_member(user)
    if not member:
        return '-'

    return member.group

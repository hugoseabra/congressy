"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def get_user_person(user):
    """ Recupera `Person` relacionado ao usuário. """
    if hasattr(user, 'person') and user.person is not None:
        return user.person
    else:
        return None


@register.simple_tag
def get_message_background_color(message):
    """ Recupera cor de fundo para messagens. """

    if message.tags == 'error':
        return '#F2DEDE'

    if message.tags == 'success':
        return '#DFF0D8'

    if message.tags == 'warning':
        return '#FCF8E3'

    if message.tags == 'info' or not message.tags:
        return '#D9EDF7'

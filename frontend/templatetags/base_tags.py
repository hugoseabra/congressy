"""
gatheros_subscription templatetags
"""
from ast import literal_eval
from django import template
from core.util import git_util

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


@register.simple_tag
def get_project_git_revision():
    """ Resgata versão de revisão do GIT do projeto. """
    return git_util.get_git_revision()


@register.filter
def get_first_item(dictionary):
    try:
        dictionary = literal_eval(dictionary.message)
        message = list(dictionary.values())[0]
        return str(message[0])
    except SyntaxError:
        return dictionary.message

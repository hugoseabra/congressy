"""
gatheros_subscription templatetags
"""
import datetime
from ast import literal_eval

import timestring
from django import template
from django.template.defaultfilters import stringfilter

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


@register.simple_tag
def to_datetime(date_string):
    """
    Return a datetime corresponding to date_string, parsed according to format.
    """
    datetime_obj = timestring.Date(date_string)
    return '{0:%Y-%m-%d %H:%M:%S}'.format(datetime_obj)


@stringfilter
@register.filter
def parse_date(date_string, format):
    """
    Return a datetime corresponding to date_string, parsed according to format.

    For example, to re-display a date string in another format::

        {{ "01/01/1970"|parse_date:"%m/%d/%Y"|date:"F jS, Y" }}

    """
    try:
        return datetime.datetime.strptime(date_string, format)
    except ValueError:
        return None


@register.filter
def money_divide(value):
    try:
        raw_result = value
        result = format(raw_result, '.2f')
        return result
    except (ValueError, ZeroDivisionError):
        return None


@register.simple_tag(name='filter_lookup')
def filter_lookup(value, arg):
    if arg not in value:
        return None
    return value[arg]

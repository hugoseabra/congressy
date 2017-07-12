"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def count_field_option_answers(option):
    """
    Recupera contagem de responstas vinculadas a uma opção de campo de
    formulário.
    """
    counter = 0
    for answer in option.field.answers.all():
        if option.value in answer.value:
            counter += 1

    return counter

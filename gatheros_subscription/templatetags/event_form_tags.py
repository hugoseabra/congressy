"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.simple_tag
def user_can_manage(user, field):
    """ Verifica se usuário pode gerenciar campos de formulário. """
    not_default = field.form_default_field is False
    can_edit = user.has_perm('gatheros_subscription.change_field', field)

    return not_default and can_edit


@register.simple_tag
def get_field_order(form, field):
    """ Recupera ordem do do campo no formulário. """
    order_list = form.get_order_list()
    counter = 1
    for field_name in order_list:
        if field.name == field_name:
            return counter

        counter += 1


@register.simple_tag
def is_inactive(form, field):
    """ Verifica se campo está inativo no formulário. """
    inactive_list = form.get_inactive_fields_list()
    return field.name in inactive_list if inactive_list else False


@register.simple_tag
def is_required(form, field):
    """ Verifica se campo obrigatório. """
    return form.is_required(field)


@register.simple_tag
def is_default_configuration(form, field):
    """ Verifica se configuração do campo no formulário é padrão. """
    config = form.required_configuration
    custom_required = config.get(field.name) if config else None
    return not is_inactive(form, field) and custom_required is None

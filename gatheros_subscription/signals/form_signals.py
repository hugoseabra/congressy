""" Signals do model `Form`. """
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import model_to_dict

from gatheros_subscription.models import DefaultField, Field, FieldOption, Form


@receiver(post_save, sender=Form)
def manage_form_fields(instance, raw, **_):
    """
    Gerencia campos de Form garantindo que todos os campos padrão estejam
    nele.

    Este Signal é importante para garantir que todas as inscrições recebam
    as informações dos campos padrão que estão diretamente ligados a Person.
    """
    # Disable when loaded by fixtures or brand entity
    if raw is True:
        return

    default_fields = DefaultField.objects.all().order_by('order')

    # Se não há campos-padrão, nada processar.
    if not default_fields:
        return

    # Se possui todos os campos padrão, nada a processar.
    if _has_all_default_fields(default_fields, instance):
        _preverse_order(default_fields, instance)
        return

    # Pega a organização correta
    organization = instance.event.organization

    for default_field in default_fields:
        field = _create_field(
            form=instance,
            organization=organization,
            **_clean_dict(default_field)
        )
        if default_field.with_options:
            options = list(default_field.options.all())
            _create_options(field, options)

    _preverse_order(default_fields, instance)


def _has_all_default_fields(default_fields, form):
    """ Verifica se formulário possui todos os campos padrão. """
    form_default_fields_list = [
        field.name for field in form.fields.filter(form_default_field=True)
    ]

    # Se não há qualquer campo padrão
    if not form_default_fields_list:
        return False

    for field in default_fields:
        if field.name not in form_default_fields_list:
            return False

    return True


def _clean_dict(saved_field):
    """ Exporta `dict` do model e normaliza-o. """
    return model_to_dict(saved_field, exclude=(
        'id',
        'order',
        '_state',
    ))


def _create_field(organization, form, **kwargs):
    """ Cria campo em formulário. """
    data = {'form_default_field': True, 'organization': organization}
    data.update(**kwargs)

    try:
        field = organization.fields.get(name=data.get('name'))

    except Field.DoesNotExist:
        field = Field.objects.create(**data)

    field.forms.add(form)
    return field


def _create_options(field, default_options):
    """ Cria opções de campo. """
    for option in default_options:
        data = {}
        data.update(**_clean_dict(option))
        data.update({'field': field})

        try:
            field.options.filter(value=data.get('value'))
        except FieldOption.DoesNotExist:
            FieldOption.objects.create(**data)


def _preverse_order(default_fields, form):
    """ Preserva orderm dos campos padrão. """
    order = form.get_order_list()

    if not order:
        form_fields = [field.name for field in form.fields.all()]
        order = form_fields

    elif _is_default_fields_ordered(default_fields, order):
        return

    updated_orders = [field.name for field in default_fields]

    for field_name in order:
        if field_name in updated_orders:
            continue

        updated_orders.append(field_name)

    form.set_order_list(updated_orders)
    form.save()


def _is_default_fields_ordered(default_fields, form_order):
    """
    Verifica se campos-padrão estão ordenados de forma correta no formulário.
    """
    for d_field in default_fields:
        if not form_order[d_field.order]:
            return False

        if d_field.name != form_order[d_field.order]:
            return False

    return True

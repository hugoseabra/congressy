from django.db.models.signals import post_save
from django.forms import model_to_dict
from django.dispatch import receiver

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

    # Pega a organização correta
    organization = instance.event.organization

    if not default_fields:
        return

    def clean_dict(saved_field):
        """ Exporta `dict` do model e normaliza-o. """
        return model_to_dict(saved_field, exclude=(
            'id',
            '_state',
        ))

    def create_field(form, **kwargs):
        """ Cria campo em formulário. """
        data = {'form_default_field': True, 'organization': organization}
        data.update(**kwargs)

        try:
            field = form.fields.get(
                organization=organization,
                name=data.get('name')
            )

        except Field.DoesNotExist:
            field = Field.objects.create(**data)
            field.forms.add(form)

        return field

    def create_options(field, default_options):
        for option in default_options:
            data = {}
            data.update(**clean_dict(option))
            data.update({'field': field})

            try:
                field.options.filter(name=data.get('name'))
            except FieldOption.DoesNotExist:
                FieldOption.objects.create(**data)

    for default_field in default_fields:
        saved = create_field(form=instance, **clean_dict(default_field))
        if default_field.with_options:
            options = list(default_field.options.all())
            create_options(saved, options)

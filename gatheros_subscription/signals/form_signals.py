from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_subscription.models import DefaultField, Field, FieldOption, Form


@receiver(post_save, sender=Form)
def mange_form_fields(instance, raw, **_):
    # Disable when loaded by fixtures or brand entity
    if raw is True:
        return

    default_fields = DefaultField.objects.all().order_by('order')

    if not default_fields:
        return

    def create_options(field, default_options):
        for option in default_options:
            data = {'field': field}
            data.update(**clean_dict(option))
            FieldOption.objects.create(**data)

    def create_field(form, **kwargs):
        data = {'form': form, 'form_default_field': True}
        data.update(**kwargs)
        return Field.objects.create(**data)

    def clean_dict(saved_field):
        field_dict = saved_field.__dict__
        del field_dict['id']
        del field_dict['_state']

        return field_dict

    form_fields = instance.fields.all().order_by('order')
    existing_fields = [f.name for f in form_fields]

    for default_field in default_fields:
        if default_field.name in existing_fields:
            continue

        saved = create_field(form=instance, **clean_dict(default_field))
        if default_field.with_options:
            options = list(default_field.options.all())
            create_options(saved, options)

from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_subscription.models import DefaultField, Field, Form


@receiver(post_save, sender=Form)
def mange_form_fields(instance, raw, **_):
    # Disable when loaded by fixtures or brand entity
    if raw is True:
        return

    default_fields = DefaultField.objects.all().order_by('order')

    if not default_fields:
        return

    def create_field(form, **kwargs):
        data = {'form': form, 'form_default_field': True}
        data.update(**kwargs)
        Field.objects.create(**data)

    def clean_dict(saved_field):
        field_dict = saved_field.__dict__
        del field_dict['id']
        del field_dict['_state']

        return field_dict

    if instance.fields.count() > 0:
        existing_field_names = []
        for f in instance.fields.all().order_by('order'):
            existing_field_names.append(f.name)

        for field in default_fields:
            if field.name in existing_field_names:
                continue

            create_field(form=instance, **clean_dict(field))

    else:
        for field in default_fields:
            create_field(form=instance, **clean_dict(field))

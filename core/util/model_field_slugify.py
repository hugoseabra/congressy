"""Gatheros slugify"""

from django.template.defaultfilters import slugify as lib_slugify


class ReservedSlugException(Exception):
    """
    Erro: quando um slug reservado é inserido pelo usuário
    """


reserved_slugs = (
    'manage',
    'login',
    'logout',
    'register',
    'cgsy-admin-18',
    'reset-password'
)


def model_field_slugify(
        model_class,
        instance,
        string,
        filter_keys=None,
        exclude_keys=None,
        slug_field='slug'):
    """Slugify string based on another string and saves slug in model"""

    if str(string).lower() in reserved_slugs:
        raise ReservedSlugException('Este nome não poderá ser utilizado.')

    original_slug = lib_slugify(string)
    if exclude_keys:
        if not isinstance(exclude_keys, dict):
            raise Exception('O parâmetro `exclude_keys` deve ser um `dict`.')

        if 'pk' not in exclude_keys and instance.pk is not None:
            exclude_keys.update({'pk': instance.pk})
    elif instance.pk is not None:
        exclude_keys = {'pk': instance.pk}

    exists = True

    slug = original_slug
    counter = 1
    while exists:

        if not filter_keys:
            filter_keys = {slug_field: slug}
        else:
            filter_keys.update({slug_field: slug})

        query_set = model_class.objects.filter(**filter_keys)

        if exclude_keys:
            query_set = query_set.exclude(**exclude_keys)

        exists = query_set.exists()

        if exists:
            slug = original_slug + '-' + str(counter)
            counter += 1

    return slug

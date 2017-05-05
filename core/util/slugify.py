from django.template.defaultfilters import slugify as lib_slugify


def slugify(model_class, slugify_from, pk=None):
    slug = lib_slugify(slugify_from)

    suffix = None
    while model_class.objects.filter(slug=slug).exclude(id=pk).exists():
        if not suffix:
            suffix = 1
        else:
            suffix += 1

        slug = slug + '-' + str(suffix)

    return slug

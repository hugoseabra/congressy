from django.template.defaultfilters import slugify


def gatheros_slugify(model_class, slugify_from, pk=None):
    slug = slugify(slugify_from)

    suffix = None
    while model_class.objects.filter(slug=slug).exclude(id=pk).exists():
        if not suffix:
            suffix = 1
        else:
            suffix += 1

        slug = slug + '-' + str(suffix)

    return slug

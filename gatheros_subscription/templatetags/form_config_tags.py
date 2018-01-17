"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.inclusion_tag('subscription/config_fields/generic.html')
def render_generic_field(field, required=False, use_required_field=True):
    if required is False and use_required_field is True:
        required = field.field.required

    return {
        'field': field,
        'label_tag': field.label_tag,
        'name': field.name,
        'help_text': field.help_text,
        'errors': field.errors,
        'required': required,
    }

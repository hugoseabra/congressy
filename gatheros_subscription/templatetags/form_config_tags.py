"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.inclusion_tag('subscription/config_fields/errors.html')
def render_errors(errors):
    return {'errors': errors}


@register.inclusion_tag('subscription/config_fields/field_errors.html')
def render_field_errors(errors):
    return {'errors': errors}


@register.inclusion_tag('subscription/config_fields/generic.html')
def render_generic_field(
        field,
        required=False,
        use_required_field=True,
        autofocus=False):
    if required is False and use_required_field is True:
        required = field.field.required

    return {
        'field': field,
        'label_tag': field.label_tag,
        'name': field.name,
        'help_text': field.help_text,
        'errors': field.errors,
        'required': required,
        'autofocus': autofocus,
    }


@register.inclusion_tag('subscription/config_fields/typeahead.html')
def render_typeahead_field(
        field,
        required=False,
        use_required_field=True,
        autofocus=False):
    return render_generic_field(**{
        'field': field,
        'use_required_field': use_required_field,
        'required': required,
        'autofocus': autofocus,
    })

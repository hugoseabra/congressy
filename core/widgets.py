"""Gatheros widgets"""

import six
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.widgets import Textarea

MULTI_EMAIL_FIELD_EMPTY_VALUES = validators.EMPTY_VALUES + ('[]',)


class MultiEmailWidget(Textarea):
    """Multi e-mail widget"""

    is_hidden = False

    # noinspection PyMethodMayBeStatic
    def prep_value(self, value):
        """ Prepare value before effectively render widget """
        if value in MULTI_EMAIL_FIELD_EMPTY_VALUES:
            return ""
        elif isinstance(value, six.string_types):
            return value
        elif isinstance(value, list):
            return "\n".join(value)
        raise ValidationError('Invalid format.')

    def render(self, name, value, attrs=None, renderer=None):
        value = self.prep_value(value)
        return super(MultiEmailWidget, self).render(name, value, attrs,
                                                    renderer)

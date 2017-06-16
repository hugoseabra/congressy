"""
Gatheros custom fields
"""

import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .widgets import MultiEmailWidget


class MultiEmailField(forms.Field):
    """Field for multi-email"""

    message = "'%s' não é um email válido."
    code = 'invalid'
    widget = MultiEmailWidget

    def to_python(self, value):
        """Normalize data to a list of strings."""

        if not value:
            return []

        return [v.strip() for v in re.split('[;,\n]', value) if v != ""]

    def validate(self, value):
        super(MultiEmailField, self).validate(value)

        for email in value:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError(self.message % email, code=self.code)

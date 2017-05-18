"""Phone number validation"""

import phonenumbers
from django.core.exceptions import ValidationError


def phone_validator(value):
    """Phone number validator using phonenumbers third-party library"""

    def is_valid(data, country_code):
        """Checks if phone numberis valid"""
        try:
            data = phonenumbers.parse(data, country_code)
            return phonenumbers.is_possible_number(data)
        except phonenumbers.NumberParseException:
            return False

    if not is_valid(value, 'BR'):
        raise ValidationError('Telefone é inválido')

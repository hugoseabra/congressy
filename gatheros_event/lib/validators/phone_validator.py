import phonenumbers
from django.core.exceptions import ValidationError
from phonenumbers import NumberParseException


def phone_validator(value):
    def is_valid(data, country_code):
        try:
            data = phonenumbers.parse(data, country_code)
            return phonenumbers.is_possible_number(data)
        except NumberParseException:
            return False

    if not is_valid(value, 'BR'):
        raise ValidationError('Telefone é inválido')

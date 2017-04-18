import phonenumbers
from django.core.exceptions import ValidationError
from phonenumbers import NumberParseException

from .validator_interface import ValidatorInterface


class PhoneValidator(ValidatorInterface):
    COUNTRY_CODE = 'BR'

    def parse_number(self, number):
        return phonenumbers.parse(number, self.COUNTRY_CODE)

    def normalize(self, data):
        return self.parse_number(data).national_number

    def is_valid(self, data):
        try:
            return phonenumbers.is_possible_number(self.parse_number(data))
        except NumberParseException:
            return False

    def validate(self, data):
        if not self.is_valid(data):
            raise ValidationError('Telefone é inválido')

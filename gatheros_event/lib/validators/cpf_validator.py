import re

from django.core.exceptions import ValidationError

from .validator_interface import ValidatorInterface


class CpfValidator(ValidatorInterface):
    def clean_data(self, data):
        return re.sub(r'[^\w]', '', data)

    def is_valid(self, data):
        d1 = 0
        d2 = 0
        i = 0
        data = self.clean_data(data)
        if len(data) < 11:
            return False

        while i < 10:
            d1, d2, i = (d1 + (int(data[i]) * (11 - i - 1))) % 11 if i < 9 else d1, (
                d2 + (int(data[i]) * (11 - i))) % 11, i + 1
        return (int(data[9]) == (11 - d1 if d1 > 1 else 0)) and (int(data[10]) == (11 - d2 if d2 > 1 else 0))

    def validate(self, data):
        data = self.clean_data(data)
        if not self.is_valid(data):
            raise ValidationError('CPF é inválido')

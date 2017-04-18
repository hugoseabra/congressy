from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .validator_interface import ValidatorInterface


class EmailValidator(ValidatorInterface):
    def clean_data(self, data):
        return data.lower()

    def is_valid(self, data):
        try:
            self.validate(data)
            return True
        except ValidationError:
            return False

    def validate(self, data):
        try:
            validate_email(self.clean_data(data))
        except ValidationError as e:
            raise e

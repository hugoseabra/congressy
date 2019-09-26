"""model validators"""

import phonenumbers
from django.core.exceptions import ValidationError
from localflavor.br.forms import BRCPFField, BRCNPJField


def cpf_validator(value):
    """Cpf validator using BRCPFField()"""

    BRCPFField().clean(value)


def cnpj_validator(value):
    """CNPJ validator using BRCNPJField()"""

    BRCNPJField().clean(value)


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

"""CPF Validator"""

from localflavor.br.forms import BRCPFField


def cpf_validator(value):
    """Cpf validator using BRCPFField()"""

    BRCPFField().clean(value)

"""CPF Validator"""

from localflavor.br.forms import BRCPFField, BRCNPJField


def cpf_validator(value):
    """Cpf validator using BRCPFField()"""

    BRCPFField().clean(value)


def cnpj_validator(value):
    """CNPJ validator using BRCNPJField()"""

    BRCNPJField().clean(value)

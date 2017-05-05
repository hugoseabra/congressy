from localflavor.br.forms import BRCPFField


def cpf_validator(value):
    BRCPFField().clean(value)

import phonenumbers
from django import forms


def clear_string(string):
    if not string:
        return ''

    return str(string) \
        .replace('.', '') \
        .replace('-', '') \
        .replace('/', '') \
        .replace('(', '') \
        .replace(')', '') \
        .replace(' ', '')


def clean_phone(phone_number):
    if not phone_number:
        return ''

    dirty_phone = clear_string(phone_number)

    if dirty_phone:

        tmp_dirty_phone = '+55' + clear_string(dirty_phone)

        phone = phonenumbers.parse(tmp_dirty_phone)

        if not phonenumbers.is_possible_number(phone) or not \
                phonenumbers.is_valid_number(phone):
            raise forms.ValidationError(
                'Telefone Inválido',
                code='invalid_phone',
                params={'phone': dirty_phone},
            )

    return dirty_phone


def clean_cellphone(phone_number, country='BR'):
    if not phone_number:
        return ''

    dirty_phone = clear_string(phone_number)

    if dirty_phone:
        # tmp_dirty_phone = '+55' + clear_string(dirty_phone)
        tmp_dirty_phone = clear_string(dirty_phone)

        if country == 'BR':
            is_cellphone = _is_brazilian_cellphone(tmp_dirty_phone)
        else:
            # Por enquanto vamos suportar telefones internacionais como
            # qualquer telefone.
            is_cellphone = True

        phone = phonenumbers.parse(tmp_dirty_phone)
        possible = phonenumbers.is_possible_number(phone)
        valid = phonenumbers.is_valid_number(phone)

        if not is_cellphone or not possible or not valid:
            raise forms.ValidationError(
                'Telefone Inválido',
                code='invalid_phone',
                params={'phone': dirty_phone},
            )

    return dirty_phone


def _is_brazilian_cellphone(number):
    """
    Verifica se número de celular começa com 9 e possui número de digitos
    corretos.
    """
    number = clear_string(number)
    # elimina número internacional
    if number.startswith('+'):
        number = number[3:]

    # elimina DDD
    number = number[2:]
    if not number[0] == '9':
        return False

    if len(number) != 9:
        return False

    return True

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
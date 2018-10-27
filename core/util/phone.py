from phonenumbers.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import format_in_original_format, \
    country_code_for_region


def get_country_code_by_region(region):
    region = str(region).upper()
    return country_code_for_region(region)


def format_phone_number(country_code, number):
    phone_number = PhoneNumber(
        country_code=country_code,
        national_number=number
    )

    # Colocando região de chamada até ver como como isso funciona
    formatted = format_in_original_format(phone_number, region_calling_from='')
    return '+{} {}'.format(country_code, formatted)

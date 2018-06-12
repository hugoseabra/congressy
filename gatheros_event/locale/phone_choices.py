from .locales import COUNTRIES


def get_country_phone_code(digits_2):
    for country in COUNTRIES:
        if country['codes']['digits_2'].upper() == str(digits_2).upper():
            return country['phone_code']
    return None


def get_phone_choices():
    return [
        (country['codes']['digits_2'], country['phone_code'])
        for country in COUNTRIES
    ]

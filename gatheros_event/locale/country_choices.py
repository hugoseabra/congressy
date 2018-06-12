from .locales import COUNTRIES


def get_country_data(digits_2):
    for country in COUNTRIES:
        if country['codes']['digits_2'].upper() == str(digits_2).upper():
            return country
    return None


def get_country_choices():
    return [
        (country['codes']['digits_2'], country['langs']['pt-br'])
        for country in COUNTRIES
    ]

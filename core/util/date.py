"""
    Helper function used in an assortment of places.
"""
from datetime import datetime


def create_years_list():

    current_year = datetime.now().year
    last_100_years = current_year - 100

    # Plus one needed to make range go to the current year, and not the
    # previous year. ie if current_year == 2018 then the range would only go
    #  to 2017.
    years = list(range(last_100_years, current_year + 1))

    return years



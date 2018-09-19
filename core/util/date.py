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


class DateTimeRange(object):
    """
    Creates a lazy range of date or datetimes. Modeled after the Python 3 range type and has
    fast path membership checking, lazy iteration, indexing and slicing. Unlike range, DateRange
    allows an open ended range. Also unlike range, it does not have an implicit step so it must be
    provided.
    """

    def __init__(self, start=None, stop=None):

        if start is None:
            raise TypeError("must provide starting point for DateTimeRange.")

        if stop is None:
            raise TypeError("must provide stopping point for DateTimeRange.")

        self.start = start
        self.stop = stop

    def __repr__(self):
        return "{!s}(start={!r}, stop={!r}".format(
            self.__class__.__name__,
            self.start,
            self.stop)

    def __contains__(self, x):
        return self.start <= x <= self.stop

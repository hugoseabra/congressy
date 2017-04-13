import calendar
import datetime

class FilterByEventMixin(object):
    """ Adiciona um método aos models para facilitar as queries por eventos """

    @classmethod
    def by_event(cls, event):
        """ Retorna uma queryset com a entidade filtrada por evento"""
        return cls.objects.filter(event=event)


def current_week_range(date):
    """ Retorna uma tupla com a data inicial e a final da semana """
    start = date - datetime.timedelta(days=date.weekday())
    end = start + datetime.timedelta(days=6)
    return start, end


def next_week_range(date):
    """ Retorna uma tupla com a data inicial e a final da  próxima semana """
    date = date + datetime.timedelta(weeks=1)
    return current_week_range(date)


def current_month_range(date):
    """ Retorna uma tupla com a data inicial e a final da  mês """

    start = date.replace(day=1)
    _, n_days = calendar.monthrange(date.year, date.month)
    end = date.replace(day=n_days)
    return start, end


def next_month_range(date):
    """ Retorna uma tupla com a data inicial e a final da próximo mês """

    if date.month == 12:
        date = date.replace(month=1)
    else:
        date = date.replace(month=date.month+1)
    return current_month_range(date)


def current_year_range(date):
    """ Retorna uma tupla com o primeiro e o ultimo dia do ano """
    start = date.replace(day=1, month=1)
    end = date.replace(day=31, month=12)
    return start, end


def filter_by_date(queryset, date):
    today = datetime.date.today()
    if date == 'tomorrow':
        tomorrow = today + datetime.timedelta(days=1)
        tomorrow = (
            datetime.datetime.combine(tomorrow, datetime.time.min),
            datetime.datetime.combine(tomorrow, datetime.time.max)
        )

        return queryset.filter(date_start__range=tomorrow)

    elif date == 'this_week':
        return queryset.filter(date_start__range=current_week_range(today))
    elif date == 'next_week':
        return queryset.filter(date_start__range=next_week_range(today))
    elif date == 'this_month':
        return queryset.filter(date_start__range=current_month_range(today))
    elif date == 'next_month':
        return queryset.filter(date_start__range=next_month_range(today))
    elif date == 'this_year':
        return queryset.filter(date_start__range=current_year_range(today))

    raise Exception('Não argumento date: "{}" inválido'.format(date))
from datetime import datetime, timedelta

import django

django.setup()

# noinspection PyPep8
from gatheros_event.models import Event


"""
11 eventos com datas reajustadas com referência a data de hoje
"""
ref_days = [
    # Arte e Agricultura Urbana
    {'days_before_today': -5, 'days_of_event': 1},
    # Django, muito al\u00e9m do Python
    {'days_before_today': 0, 'days_of_event': 1},
    # SEO e Resultados
    {'days_before_today': 5, 'days_of_event': 1},
    # Streaming de Sucesso
    {'days_before_today': 8, 'days_of_event': 1},
    # Eu Mando Nudes - By lots
    {'days_before_today': 15, 'days_of_event': 1},
    # Mulheres de Sucesso
    {'days_before_today': 25, 'days_of_event': 1},
    # Encontro de L\u00edderes 2017
    {'days_before_today': 30, 'days_of_event': 1},
    # Encontro de Casais 2017
    {'days_before_today': 35, 'days_of_event': 3},
]

events = Event.objects.all().order_by('pk')
for i, dict_day in enumerate(ref_days):
    event = events[i]
    start = datetime.today() + timedelta(
        days=dict_day.get('days_before_today')
    )

    end = start + timedelta(days=dict_day.get('days_of_event') - 1)

    event.date_start = start.replace(hour=8, minute=0, second=0)
    event.date_end = end.replace(hour=18, minute=0, second=0)
    published = event.published
    event.published = False
    event.save()

    event.published = published
    event.save()

"""
Datas dos lotes devem começar e terminar antes da data inicial do evento.

São 11 eventos com seus respectivos lotes organizados nos fixtures.
"""
lots_dates = [
    # Arte e Agricultura Urbana
    [{'days_before_event': 15, 'days': 15}],
    # Django, muito al\u00e9m do Python
    [{'days_before_event': 15, 'days': 15}],
    # SEO e Resultados
    [{'days_before_event': 15, 'days': 15}],
    # Streaming de Sucesso
    [{'days_before_event': 15, 'days': 15}],
    # Eu Mando Nudes - By lots
    [
        {'days_before_event': 45, 'days': 15},  # Lote 1
        {'days_before_event': 30, 'days': 15},  # Lote 2
        {'days_before_event': 15, 'days': 15},  # Lote 3
        {'days_before_event': 45, 'days': 45},  # Parceiros
    ],
    # Mulheres de Sucesso
    [{'days_before_event': 5, 'days': 5}],
    # Encontro de L\u00edderes 2017
    [{'days_before_event': 30, 'days': 30}],
    # Encontro de Casais 2017
    [{'days_before_event': 50, 'days': 50}],
]

for i, dict_dates in enumerate(lots_dates):
    event = events[i]

    if dict_dates is None:
        continue

    ii = 0
    for lot in event.lots.all():

        try:

            if not dict_dates[ii]:
                raise Exception('Configuração errada para {}'.format(lot))

            ref = dict_dates[ii]

            start = event.date_start - timedelta(
                days=ref.get('days_before_event') - 1)
            end = start + timedelta(days=ref.get('days') - 1)

            if end >= event.date_start:
                end = event.date_start - timedelta(seconds=1)
            else:
                end = end.replace(hour=23, minute=59, second=59)

            lot.date_start = start.replace(hour=0, minute=0, second=0)
            lot.date_end = end
            lot.save()

            ii += 1
        except IndexError:
            pass


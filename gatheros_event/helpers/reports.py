from django.db import models
from kanu_locations.models import City


def get_report_gender(queryset):
    subs = queryset.values(
        'person__gender',
    ).annotate(
        num_gender=models.Count('person__gender')
    ).order_by()

    men = [
        sub['num_gender'] for sub in subs if sub['person__gender'] == 'M'
    ]

    women = [
        sub['num_gender'] for sub in subs if sub['person__gender'] == 'F'
    ]

    return {
        'men': sum(men),
        'women': sum(women),
    }


def get_report_pne(queryset):
    subs = queryset.values(
        'person__pne',
    ).annotate(
        num_pnes=models.Count('person__pne'),
    ).order_by()

    return sum([sub['num_pnes'] for sub in subs if sub['person__pne'] is True])


def get_report_cities(queryset):
    queryset = queryset.values('person__city_id').distinct()

    city_pk_nums = {}
    city_pks = []
    for city_dict in queryset:
        pk = city_dict['person__city_id']
        if pk not in city_pk_nums:
            city_pk_nums[pk] = 0
            city_pks.append(pk)

        city_pk_nums[pk] += 1

    cities = City.objects.filter(pk__in=city_pks)

    report_cities = []
    for city in cities:
        report_cities.append({
            'name': '{}-{}'.format(city.name, city.uf),
            'num': city_pk_nums[city.pk]
        })

    return report_cities

def get_report_age(queryset):
    ages = {
        'under_15' : 0,
        'bet_16_20': 0,
        'bet_21_30': 0,
        'bet_31_40': 0,
        'bet_41_60': 0,
        'over_61': 0
    }
    for sub in queryset.all():
        age = sub.person.age
        if not age:
            continue

        if age <= 15:
            ages['under_15'] += 1

        elif age >15 and age <=20:
            ages['bet_16_20'] += 1

        elif age >21 and age <=30:
            ages['bet_21_30'] += 1

        elif age >31 and age <=40:
            ages['bet_31_40'] += 1

        elif age >41 and age <=60:
            ages['bet_41_60'] += 1

        elif age > 60:
            ages['over_61'] += 1

    return ages

from django.core.checks import register, Warning
from django.conf import settings

from django.db import connection


def select_extension(name):
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from pg_available_extensions "
            "where name=%s and not installed_version is null",
                       [name])
        row = cursor.fetchone()

    return row


@register()
def example_check(app_configs, **kwargs):
    errors = []

    if not select_extension('unaccent'):
        errors.append(
            Warning(
                'A extesão do Postgresql "unaccent" não está instalada',
                hint='psql {0} -c \'CREATE EXTENSION "unaccent";\''.format(
                    settings.DATABASES['default']['NAME']),
            )
        )

    return errors

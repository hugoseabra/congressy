import os
import sys

from django.core.management.utils import get_random_secret_key

sys.path.append("..")

from scripts import setup

SENTRY_PRIVATE_DSN = os.environ.get('SENTRY_PRIVATE_DSN')

dbname = os.environ.get('DBNAME')
dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS', '')
dbhost = os.environ.get('DBHOST')
dbport = os.environ.get('DBPORT', 5432)

if not SENTRY_PRIVATE_DSN:
    print("SENTRY_PRIVATE_DSN not provided or misconfigured.")
    sys.exit(1)

if not dbhost or not dbuser or dbpass is None or not dbname:
    print(
        "DB credentials not provided or misconfigured:"
        " -e DBHOST=host -e DBUSER=user -e DBPASS=password -e DBNAME=dbname"
        " -e DBPORT=5432"
    )
    sys.exit(1)


def read_file(file_path):
    if not os.path.exists(file_path):
        return ''

    with open(file_path) as f:
        content = f.read()
        f.close()

        return content.rstrip('\r\n')


# create dictionary of environment variables
env_dict = {
    'SENTRY_PRIVATE_DSN': SENTRY_PRIVATE_DSN,
    'DBNAME': dbname,
    'DBUSER': dbuser,
    'DBPASS': dbpass,
    'DBHOST': dbhost,
    'DBPORT': dbport,
    'SECRET_KEY': 'jq0m!8!um0yva5i5b!!j(imcu148gco-w+pe_y2k)wdg9x67t8',
    # 'SECRET_KEY': get_random_secret_key(),
    'APP_VERSION': read_file('/var/www/cgsy/version'),
}

# Manage
setup(
    env_dict,
    '/var/www/cgsy/project/manage/settings/common.py',
    '/var/www/cgsy/project/manage/settings/common.py'
)

setup(
    env_dict,
    '/var/www/cgsy/project/manage/settings/prod.py',
    '/var/www/cgsy/project/manage/settings/prod.py'
)

# Partner
setup(
    env_dict,
    '/var/www/cgsy/project/partner/settings/prod.py',
    '/var/www/cgsy/project/partner/settings/prod.py'
)

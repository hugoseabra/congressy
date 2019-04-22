import os
import sys

sys.path.append(sys.path.append(os.path.dirname(os.path.dirname(__file__))))

# from django.core.management.utils import get_random_secret_key

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

rabbitmq_user = os.environ.get('RABBITMQ_USER')
rabbitmq_pass = os.environ.get('RABBITMQ_PASS')
rabbitmq_server = os.environ.get('RABBITMQ_SERVER')

if not rabbitmq_user or not rabbitmq_pass or not rabbitmq_server:
    print(
        "RABBITMQ configuration not provided or misconfigured:"
        " -e RABBITMQ_USER=user -e RABBITMQ_PASS=pass"
        " -e RABBITMQ_SERVER=server"
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
    'APP_VERSION': read_file('/code/version'),
    'RABBITMQ_USER': rabbitmq_user,
    'RABBITMQ_PASS': rabbitmq_pass,
    'RABBITMQ_SERVER': rabbitmq_server,
}

# Manage
setup(
    env_dict,
    '/code/project/manage/settings/common.py',
    '/code/project/manage/settings/common.py'
)

setup(
    env_dict,
    '/code/project/manage/settings/prod.py',
    '/code/project/manage/settings/prod.py'
)

# Partner
setup(
    env_dict,
    '/code/project/partner/settings/prod.py',
    '/code/project/partner/settings/prod.py'
)

# Admin
setup(
    env_dict,
    '/code/project/admin_intranet/settings/common.py',
    '/code/project/admin_intranet/settings/common.py'
)

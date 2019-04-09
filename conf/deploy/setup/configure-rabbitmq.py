import os
import sys

sys.path.append("..")

from scripts import setup

rabbitmq_server = os.environ.get('RABBITMQ_SERVER')

if not rabbitmq_server:
    print(
        "RABBITMQ_SERVER not provided or misconfigured:"
        " -e RABBITMQ_SERVER=server_host"
    )
    sys.exit(1)

# create dictionary of environment variables
env_dict = {
    'RABBITMQ_SERVER': rabbitmq_server,
}

setup(
    env_dict,
    '/var/www/cgsy/project/manage/settings/prod.py',
    '/var/www/cgsy/project/manage/settings/prod.py'
)

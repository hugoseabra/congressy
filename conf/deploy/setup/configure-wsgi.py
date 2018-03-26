import os
import sys

sys.path.append("..")

from scripts import setup

# create dictionary of environment variables
env_dict = {
    'DJANGO_SETTINGS_MODULE': os.getenv(
        'DJANGO_SETTINGS_MODULE',
        'project.settings.prod'
    ),
}

setup(
    env_dict,
    '/var/www/cgsy/conf/deploy/templates/wsgi.j2',
    '/var/www/cgsy/project/wsgi.py'
)

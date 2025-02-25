import os
import sys

sys.path.append(os.path.join('/', 'code', 'conf', 'deploy'))

from scripts import setup

# create dictionary of environment variables
env_dict = {
    'DJANGO_SETTINGS_MODULE': os.getenv(
        'DJANGO_SETTINGS_MODULE',
        'project.settings.staging'
    ),
}

setup(
    env_dict,
    '/code/conf/staging/templates/wsgi.j2',
    '/code/project/wsgi.py'
)

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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
    '/code/conf/deploy/templates/wsgi.j2',
    '/code/project/wsgi.py'
)

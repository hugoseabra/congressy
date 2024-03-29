# pylint: skip-file
"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

BASE = os.path.dirname(os.path.dirname(os.path.join(__file__)))
VERSION_FILE_PATH = os.path.join(BASE, 'version')
if os.path.exists(VERSION_FILE_PATH):
    f = open(VERSION_FILE_PATH)
    version = f.read()
    f.close()
    version = version.rstrip('\r\n') if version else 'dev'
    os.environ.setdefault("ENVIRONMENT_VERSION", version.rstrip('\r\n'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.manage.settings.dev")

application = get_wsgi_application()

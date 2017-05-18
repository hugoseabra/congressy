# pylint: skip-file
from .dev import *

DATABASES['default']['NAME'] = 'gatheros_site_teste'

AUTHENTICATION_BACKENDS.append('core.tests.auth.TestcaseUserBackend')

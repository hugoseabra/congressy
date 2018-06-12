# pylint: skip-file
from project.base_settings import *

# ========================== BASE CONFIGURATION ============================= #
ROOT_URLCONF = 'project.partner.urls'
# ================================= APPS ==================================== #
INSTALLED_APPS += [
    'gatheros_event',
    'gatheros_subscription',
    'payment_debt',
    'payment',
    'mailer',
    'partner',
    'survey',
]
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

SITE_ID = 2

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# @TODO Mudar para /media em produção.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
# ============================== FIXTURES =================================== #
FIXTURE_DIRS += [
    os.path.join(BASE_DIR, 'project', 'partner', 'fixtures'),
]
# ========================== PARTNER ======================================== #
# Valor maximo em que a soma de todos os parceiros do evento não deve
# ultrapassar do rateamento do montante da Congressy
PARTNER_MAX_PERCENTAGE_IN_EVENT = 20.00

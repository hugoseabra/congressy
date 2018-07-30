# pylint: skip-file
from project.base_settings import *

# ========================== BASE CONFIGURATION ============================= #
ROOT_URLCONF = 'project.admin_intranet.urls'
# ================================= APPS ==================================== #
INSTALLED_APPS += [
    'admin_intranet',
    'gatheros_event',
    'gatheros_subscription',
    'gatheros_front',
    'mailer',
    'payment_debt',
    'payment',
    'partner',
    'hotsite',
    'survey',
    'addon',
    'associate',
    # 'bitly',
    'scientific_work',
    'certificate',
    'raffle',
    'csv_importer',
]
# =========================== AUTH BACKENDS ================================= #
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_SUPERUSER_ONLY = True
ACCOUNT_REGISTRATION = False
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

SITE_ID = 3

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# @TODO Mudar para /media em produção.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
# ============================== FIXTURES =================================== #
FIXTURE_DIRS += [
    os.path.join(BASE_DIR, 'project', 'admin_intranet', 'fixtures'),
]
# ========================== PARTNER ======================================== #
# Valor maximo em que a soma de todos os parceiros do evento não deve
# ultrapassar do rateamento do montante da Congressy
PARTNER_MAX_PERCENTAGE_IN_EVENT = 20.00

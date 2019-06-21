# pylint: skip-file
from project.base_settings import *

# ========================== BASE CONFIGURATION ============================= #
ROOT_URLCONF = 'project.manage.urls'
# ================================= APPS ==================================== #
INSTALLED_APPS += [
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
    'importer',
    'attendance',
    'service_tags',
    'mix_boleto',
    'installment',
    'cgsy_commands',
    'sync',
]
# =========================== AUTH BACKENDS ================================= #
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/manage/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_SUPERUSER_ONLY = False
ACCOUNT_REGISTRATION = True
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

SITE_ID = 1

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# @TODO Mudar para /media em produção.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
# ============================== FIXTURES =================================== #
FIXTURE_DIRS += [
    os.path.join(BASE_DIR, 'project', 'manage', 'fixtures'),
    os.path.join(BASE_DIR, 'gatheros_event', 'tests', 'fixtures'),
    os.path.join(BASE_DIR, 'gatheros_subscription', 'tests', 'fixtures'),
    os.path.join(BASE_DIR, 'payment', 'tests', 'fixtures'),
    os.path.join(BASE_DIR, 'addon', 'tests', 'fixtures'),
    os.path.join(BASE_DIR, 'survey', 'tests', 'fixtures'),
]
# ============================= TEMPLATES =================================== #
TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'gatheros_event.context_processors.account',
)

# ============================ GOOGLE RECAPTCHA ============================= #
GOOGLE_RECAPTCHA_SECRET_KEY = '6Lerw18UAAAAAGJyU5G_3CZN6Et4ZTcIhLiUhawX'

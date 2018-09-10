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
# ============================= PAYMENT ===================================== #
# Planos da congressy, contemplam percentuais de recebimento em cima das
# transações

# Valor mínimo que a congrssy deve receber por transação. Se o valor do recebi
# devido for menor do que este, o valor da transaçaõ da parte da congressy será
# este valor.
CONGRESSY_MINIMUM_AMOUNT = 4.99

# Taxas de juros de parcelamento de valores da Congressy.
CONGRESSY_INSTALLMENT_INTERESTS_RATE = 2.29
GOOGLE_RECAPTCHA_SECRET_KEY = '6Lerw18UAAAAAGJyU5G_3CZN6Et4ZTcIhLiUhawX'
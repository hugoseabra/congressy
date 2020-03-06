# pylint: skip-file
from django.urls import reverse_lazy

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
LOGIN_URL = reverse_lazy('public:login')
LOGIN_REDIRECT_URL = '/manage/'
LOGOUT_REDIRECT_URL = reverse_lazy('public:login')
LOGIN_SUPERUSER_ONLY = False
ACCOUNT_REGISTRATION = True
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

SITE_ID = os.getenv('SITE_ID', 1)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static-manage/'

# @TODO Mudar para /media em produção.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media-manage/'
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
GOOGLE_RECAPTCHA_PUBLIC_KEY = '6Lerw18UAAAAANaVK-G5QZEM2My-iumnxVFbDrpZ'
GOOGLE_RECAPTCHA_SECRET_KEY = '6Lerw18UAAAAAGJyU5G_3CZN6Et4ZTcIhLiUhawX'

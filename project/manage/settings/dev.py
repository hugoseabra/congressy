# pylint: skip-file

from . import *
from project.frontend import get_frontend_loader

# ========================== BASE CONFIGURATION ============================= #

SECRET_KEY = '1@==vhll7d5v(%=t++oy-38+639o-4*f73^!o=v!a^z$#(6x%$'

DEBUG = True
# ========================= SERVER CONFIGURATION ============================ #
ABSOLUTEURI_PROTOCOL = 'http'
# ================================= APPS ==================================== #
INSTALLED_APPS.extend([
    'debug_toolbar',
    'django_extensions',
])

if os.getenv('OFFLINE_SERVER') == 'True':
    # CONGRESSY - Sincronização de servidores offline
    INSTALLED_APPS.extend([
        'sync_client',
    ])
# ============================== DATABASE =================================== #
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cgsyplatform',
        'USER': 'congressy',
        'PASSWORD': 'congressy',
        'HOST': 'localhost',
    },
}
# ============================= MIDDLEWARES ================================= #
# Django debug toolbar
MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
# ================================= E-MAIL ================================== #
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# Host for sending e-mail.
EMAIL_HOST = 'localhost'
# Port for sending e-mail.
EMAIL_PORT = 1025
# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
# ============================== GOOGLE ===================================== #
GOOGLE_MAPS_API_KEY = 'AIzaSyD6ejnl_NChhfZhI_GoNT12FfCVCdOlgtw'
# ================================ PAGAR.ME ================================= #
PAGARME_API_KEY = 'ak_test_IkLKxOIdD0GVTHfmlSPA1zuGoaCQtd'
PAGARME_ENCRYPTION_KEY = 'ek_test_ep7xk51I1XtWg58B9xij1VFwJRLcKa'
PAGARME_RECIPIENT_ID = 're_cjcupb1iq0200zl6d89r92s32'
PAGARME_TEST_RECIPIENT_ID = 're_cjdagxm5q00fqok6eeuukmmtp'
# ============================ DEBUG TOOL BAR ================================ #
INTERNAL_IPS = ['127.0.0.1']

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda r: False,  # disables it
}

# ============================ WKHTMLTOPDF  ================================== #
WKHTMLTOPDF_WS_URL = 'http://localhost:5010'

# ================================ CELERY ==================================== #
CELERY_BROKER_URL = 'amqp://cgsy:cgsy@localhost:5672//'
# CELERY_RESULT_BACKEND = 'amqp://cgsy:cgsy@localhost:5672/'

# ======================== HEALTH CHECK - RABBITMQ ========================== #
BROKER_URL = CELERY_BROKER_URL

# ============================== VIDEOS ===================================== #
CGSY_VIDEOS_API_ADMIN_TOKEN = '4352cababfd0f7912869a5c7d2b90144e963dff1'
CGSY_VIDEOS_API_URL = 'http://localhost:8001'

# ============================ FRONTEND ===================================== #
FRONTEND_DEBUG = os.getenv('FRONTEND_DEBUG', DEBUG)
frontend_loader = get_frontend_loader(
    front_end_dir_path=os.path.join(BASE_DIR, 'frontend', 'vue_frontend'),
    debug_mode=eval(str(FRONTEND_DEBUG)) is True,
)
WEBPACK_LOADER = dict(frontend_loader)

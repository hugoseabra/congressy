# pylint: skip-file
import os

from django.contrib.messages import constants as message_constants
from django.utils.translation import ugettext_lazy as _

# ========================== BASE CONFIGURATION ============================= #
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DEBUG = False
ROOT_URLCONF = 'project.urls'
# ================================= APPS ==================================== #
INSTALLED_APPS = [
    # DJANGO_APPS
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.humanize',

    # Django added apps
    'django.contrib.sites',
    'django.forms',

    # THIRD PARTY
    'absoluteuri',
    'permission',
    'stdimage',
    'ckeditor',
    'datetimewidget',
    'widget_tweaks',
    'django_user_agents',
    'rest_framework',
    'rest_framework.authtoken',
    'captcha',
    'wkhtmltopdf',
    'django_cron',

    # KANU_APPS
    'kanu_locations',

    # CONGRESSY APPS
    'frontend',
    'gatheros_event',
    'gatheros_subscription',
    'gatheros_front',
    'mailer',
    'payment',
    'core',
    'hotsite',
    'partner',
]
# ================= LOCATION/LANGUAGES/INTERNATIONALIZATION ================= #
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Tell Django where the project's translation files should be.
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LANGUAGES = (
    ('en', _('English')),
    ('en-us', _('English (US)')),
    ('pt-br', _('Português')),
)
# ============================= MIDDLEWARES ================================= #

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]
# =========================== AUTH BACKENDS ================================= #
AUTHENTICATION_BACKENDS = [
    # auth
    'django.contrib.auth.backends.ModelBackend',
    # django-permission
    'permission.backends.PermissionBackend',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/manage/'
LOGOUT_REDIRECT_URL = '/login/'
# ============================ VALIDATORS =================================== #
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
]
# ========================= SERVER CONFIGURATION ============================ #
WSGI_APPLICATION = 'project.wsgi.application'

ALLOWED_HOSTS = ['*']
X_FRAME_OPTIONS = 'ALLOWALL'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']

SITE_ID = 1

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
# Uncomment this when cache is configured
# USER_AGENTS_CACHE = 'default'

# ============================= TEMPLATES =================================== #
# Added to allow overriding django forms templates.
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


class InvalidTemplateVariable(str):
    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError
        # access to current settings
        from django.conf import settings

        # display the message on page in make log it only on stage development
        if settings.DEBUG is False:
            raise TemplateSyntaxError("Invalid variable : '{}'".format(other))


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'core', 'forms', 'templates'),
            os.path.join(BASE_DIR, 'frontend', 'templates'),
            os.path.join(BASE_DIR, 'gatheros_event', 'templates'),
            os.path.join(BASE_DIR, 'hotsite', 'templates'),
            os.path.join(BASE_DIR, 'mailer', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            # 'string_if_invalid': InvalidTemplateVariable("%s"),
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'project.context_processors.environment_version',
                'gatheros_event.context_processors.account',
            ],
            'builtins': [
                'permission.templatetags.permissionif',
            ],
        },
    },
]
# ============================== DATABASE =================================== #
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gatheros_site',
        'USER': 'MUDAR_USUARIO',
        'PASSWORD': 'MUDAR_SENHA',
        'HOST': 'localhost',
        'PORT': '',
    },
}
# ============================== LOGGING ==================================== #
# Disable
# LOGGING_CONFIG = None
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s '
#                       '%(process)d %(thread)d %(message)s'
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose'
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'ERROR',
#             'handlers': ['console'],
#             'propagate': False,
#         },
#     },
# }
# ============================== FIXTURES =================================== #
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
    os.path.join(BASE_DIR, 'fixtures', 'workflows'),
    os.path.join(BASE_DIR, 'gatheros_event/tests/fixtures'),
    os.path.join(BASE_DIR, 'gatheros_subscription/tests/fixtures'),
    os.path.join(BASE_DIR, 'payment/tests/fixtures'),
]
# ============================= CKEDITOR ==================================== #
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar_Full': [
            '/',
            {
                'name': 'styles',
                'items': [
                    'Styles',
                    'Format',
                    'FontSize'
                ]
            },
            {
                'name': 'basicstyles',
                'items': [
                    'Bold',
                    'Italic',
                    'Underline',
                    'Strike',
                    '-',
                    'RemoveFormat'
                ]
            },
            {
                'name': 'paragraph',
                'items': [
                    'NumberedList',
                    'BulletedList',
                    '-',
                    'Outdent',
                    'Indent',
                    '-',
                    'JustifyLeft',
                    'JustifyCenter',
                    'JustifyRight',
                    'JustifyBlock'
                ]
            },
            {
                'name': 'links',
                'items': [
                    'Link',
                    'Unlink',
                    'Anchor'
                ]
            },
            {
                'name': 'insert',
                'items': [
                    'Table',
                    'HorizontalRule'
                ]
            },
            {
                'name': 'youcustomtools',
                'items': [
                    'Preview',
                    'Maximize',
                    'Source',
                ]
            },
        ],
        'toolbar': 'Full',
        'width': '100%',
        'height': 150,
    },
}
# ============================= MESSAGES ==================================== #
MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}
# =============================== E-MAIL ==================================== #
DEFAULT_FROM_EMAIL = 'Congressy <mail@congressy.net>'
CONGRESSY_REPLY_TO = 'Congressy <congressy@congressy.com>'
DEV_ALERT_EMAILS = ['Infra Congressy <infra@congressy.com>']
SALES_ALERT_EMAILS = [
    'Congressy SAC <congressy@congressy.com>',
    'Infra Congressy <infra@congressy.com>'
]
# ============================ WKHTML PDF =================================== #
WKHTMLTOPDF_CMD = os.path.join(
    BASE_DIR, "bin", "wkhtmltox", "bin", 'wkhtmltopdf'
)

# =========================== CRON CLASSES ================================== #
ALLOW_PARALLEL_RUNS = True
FAILED_RUNS_CRONJOB_EMAIL_PREFIX = "[Server check]: "

CRON_CLASSES = [
    "payment.cron.MyCronJob",
]
# ============================= PAYMENT ===================================== #
# Planos da congressy, contemplam percentuais de recebimento em cima das
# transações

# Valor mínimo que a congrssy deve receber por transação. Se o valor do recebi
# devido for menor do que este, o valor da transaçaõ da parte da congressy será
# este valor.
CONGRESSY_MINIMUM_AMOUNT = 4.99
# ========================== PARTNER ======================================== #
# Valor maximo em que a soma de todos os parceiros do evento não deve
# ultrapassar do rateamento do montante da Congressy
PARTNER_MAX_PERCENTAGE_IN_EVENT = 20.00

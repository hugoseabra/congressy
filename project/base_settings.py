# pylint: skip-file
import os

from django.contrib.messages import constants as message_constants
from django.utils.translation import ugettext_lazy as _

from core.database.postgresql import patch_unaccent

# Patch para buscas no postgresql
patch_unaccent()

# ========================== BASE CONFIGURATION ============================= #
BASE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..',
))
DEBUG = False
# ================================= APPS ==================================== #
INSTALLED_APPS = [
    # ADMIN TEMPLATE
    'grappelli',

    # DJANGO_APPS
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.humanize',

    # Healthchecks
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.psutil',
    'health_check.contrib.rabbitmq',
    'health_check.contrib.celery',

    # Django added apps
    'django.contrib.admindocs',
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
    'formtools',
    'django_cron',
    'corsheaders',

    'django_grappelli_custom_autocomplete',

    # KANU_APPS
    'kanu_locations',

    # CONGRESSY APPS - GLOBALS
    'core',
    'base',
    'frontend',
    'buzzlead',
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

USE_THOUSAND_SEPARATOR = False

FORMAT_MODULE_PATH = [
    'project.currency_formats',
]
# ============================= MIDDLEWARES ================================= #
MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    # Middleware para saber de qual host que veio a resposta do Django
    'project.manage.middleware.OriginMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

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

# django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
# CORS_ORIGIN_WHITELIST = (
#     'localhost:3030',
# )
# CORS_ORIGIN_REGEX_WHITELIST = (
#     'localhost:3030',
# )

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
            os.path.join(BASE_DIR, 'bitly', 'templates'),
            os.path.join(BASE_DIR, 'admin_intranet', 'templates'),
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
                'frontend.context_processors.render_app_only',
                'frontend.context_processors.is_debug_mode',
                'frontend.context_processors.is_offline_server',
            ],
            'builtins': [
                'permission.templatetags.permissionif',
            ],
        },
    },
]
# ============================== FIXTURES =================================== #
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
    os.path.join(BASE_DIR, 'fixtures', 'workflows'),
]
# ============================= CKEDITOR ==================================== #
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar_Custom': [
            '/',
            {
                'name': 'styles',
                'items': [
                    'Format',
                    'FontSize'
                ]
            },
            {
                'name': 'clipboard',
                'items': [
                    'Cut',
                    'Copy',
                    'Paste',
                    'PasteText',
                    'PasteFromWord',
                    '-',
                    'Undo',
                    'Redo'
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
                    'HorizontalRule',
                    'Youtube',
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
        'toolbar': 'Custom',
        'extraPlugins': ','.join([
            'youtube',
        ]),
        'width': '100%',
        'height': 150,
    },
}

# =============================== CACHE ===================================== #
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
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
    'Wyndson Oliveira <wyndson@congressy.com>',
    'Infra Congressy <infra@congressy.com>'
]
# ========================= HEALTH CHECK - PSUTILS ========================== #
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,    # in MB
}
# ============================== LOGGING ==================================== #
CGSY_LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# ============================ WKHTML PDF =================================== #
WKHTMLTOPDF_CMD = os.path.join(
    BASE_DIR, "bin", "wkhtmltox", "bin", 'wkhtmltopdf'
)

# ================= ADMIN THEME TEMPLATE - GRAPELLI ========================= #
GRAPPELLI_ADMIN_TITLE = 'CONGRESSY'
GRAPPELLI_SWITCH_USER = True
# =========================== CRON CLASSES ================================== #
ALLOW_PARALLEL_RUNS = True
FAILED_RUNS_CRONJOB_EMAIL_PREFIX = "[Server check]: "

CRON_CLASSES = [
    "payment.cron.SubscriptionStatusIrregularityTestJob",
    "payment.cron.SubscriptionPaidAndIncomplete",
    "payment.cron.CheckPayables",
]
# =============================== BITLY ===================================== #
BITLY_LOGIN = 'congressy'
BITLY_API_KEY = 'R_90819c7eac3f4c039e5f9c37f6786dda'
BITLY_ACCESS_TOKEN = '5e9398fb6cc39e8dee301f9c0192959563b8bd02'
# Tempo em que o relatório de cada link irá renovar os dados.
BITLY_TIMEOUT_STATS = 30
# ========================== PARTNER ======================================== #
# Valor maximo em que a soma de todos os parceiros do evento não deve
# ultrapassar do rateamento do montante da Congressy
# PARTNER_MAX_PERCENTAGE_IN_EVENT = 20.00

# @TODO remover. INserido provisionariamente - GYM Brasil
PARTNER_MAX_PERCENTAGE_IN_EVENT = 60.00

# ============================= PAYMENT ===================================== #
# Planos da congressy, contemplam percentuais de recebimento em cima das
# transações

# Valor mínimo que a congrssy deve receber por transação. Se o valor do recebi
# devido for menor do que este, o valor da transaçaõ da parte da congressy será
# este valor.
CONGRESSY_MINIMUM_AMOUNT = 3.49

# Taxas de juros de parcelamento de valores da Congressy.
CONGRESSY_INSTALLMENT_INTERESTS_RATE = 2.29

# Valor minimo para cada parcela
CONGRESSY_MINIMUM_AMOUNT_FOR_INSTALLMENTS = 10

# ============================ BUZZLEAD ===================================== #
BUZZLEAD_MANAGER_EMAIL = 'cto@buzzlead.com.br'

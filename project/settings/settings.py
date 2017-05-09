import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

SECRET_KEY = '1@==vhll7d5v(%=t++oy-38+639o-4*f73^!o=v!a^z$#(6x%$'

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # DJANGO_APPS
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # THIRD PARTY
    'formtools',

    # KANU_APPS
    'kanu_locations',

    # GATHEROS_APPS
    'core',
    'gatheros_event',
    'gatheros_subscription',
    'gatheros_front',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # GATHEROS_MIDLWARE_CLASSES
    'core.helper.account.middleware.CurrentSessionMiddleware',
    'core.helper.account.middleware.CurrentUserMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Gatheros user_context processor
                'gatheros_front.processor.user_context'
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

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

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
    os.path.join(BASE_DIR, 'gatheros_event/tests/fixtures'),
    os.path.join(BASE_DIR, 'gatheros_subscription/tests/fixtures'),
]

LOGIN_URL = '/entrar/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/entrar/'

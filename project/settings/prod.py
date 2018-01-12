# pylint: skip-file

from . import *

INSTALLED_APPS.append('celery')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cgsy',
        'USER': 'cgsy',
        'PASSWORD': 'CgsyAdmin!@#qwe',
        'PORT': 5432,
        'HOST': 'postgres',  # Docker host
    },
}

ABSOLUTEURI_PROTOCOL = 'https'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

SPARKPOST_API_KEY = '6dacd78f4c49080da7bbe942d4f36dc95d0c110a'
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'

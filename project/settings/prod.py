# pylint: skip-file

from . import *

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

EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'

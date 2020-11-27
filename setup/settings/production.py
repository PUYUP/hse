from .base import *
from .project import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = True
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '[::1]',
    'console.ptk-hsse.com'
]


# SENTRY
sentry_sdk.init(
    dsn="https://fc8ad650d89f42a0be005a19b401449a@o400235.ingest.sentry.io/5419903",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)


# REDIS
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'


"""
# Django Sessions
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.2/ref/settings/
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False

SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 5
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
"""


# Django csrf
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.2/ref/csrf/
CSRF_COOKIE_DOMAIN = '.ptk-hsse.com'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = [
    '.ptk-hsse.com'
]


# Django CORS
# ------------------------------------------------------------------------------
# https://pypi.org/project/django-cors-headers/
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS = [
#     'http://hse-backend.herokuapp.com.com'
# ]


# Static files (CSS, JavaScript, Images)
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hse_db',
        'USER': 'hse_db_user',
        'PASSWORD': '6+Zwx37G3)EhSx',
        'HOST': '127.0.0.1',   # Or an IP Address that your DB is hosted on
        'PORT': '',
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    }
}


# SENDGRID
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


# CHANNELS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}


# CACHING SERVER
CACHES['default']['LOCATION'] = REDIS_URL


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]

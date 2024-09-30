"""
Django settings for pelp project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
import sentry_sdk
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', False) in [1, '1', True, 'True', 'true']

SENTRY_ENABLED = False
SENTRY_DSN = os.getenv('SENTRY_DSN')
SENTRY_SAMPLE_RATE = 1.0
SENTRY_DEBUG = DEBUG
SENTRY_RELEASE = os.getenv('SENTRY_RELEASE')
SENTRY_ENVIRONMENT = os.getenv('SENTRY_ENVIRONMENT')
SENTRY_SERVER_NAME = os.getenv('SENTRY_SERVER_NAME')

if os.getenv('SENTRY_ENABLED', False) in [1, '1', 'True', True, 'true'] and os.getenv('SENTRY_DSN') is not None:
    SENTRY_ENABLED = True
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=SENTRY_SAMPLE_RATE,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,

        max_breadcrumbs=50,
        debug=SENTRY_DEBUG,
        release=os.getenv('SENTRY_RELEASE'),
        environment=os.getenv('SENTRY_ENVIRONMENT'),
        server_name=os.getenv('SENTRY_SERVER_NAME'),
        attach_stacktrace=True,
    )


def get_secret(key, value=None):

    key_value = os.environ.get(key, None)

    if key_value is None:
        # Check secrets
        key_value = None

    if key_value is None:
        # Set provided default value
        key_value = value

    return key_value


LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('ROOT_LOG_LEVEL', 'WARNING'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret("DJANGO_SECRET", None)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', [])
if isinstance(ALLOWED_HOSTS, str):
    ALLOWED_HOSTS = ALLOWED_HOSTS.split(',')

if SECRET_KEY is None and DEBUG:
    SECRET_KEY = 'django-insecure-6wv9+(=byer4fz@^b1ahj8!z#h$2gr*!y%!(6d%6ssv^+9g^^p'
if len(ALLOWED_HOSTS) == 0 and DEBUG:
    ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_prometheus',
    #'fontawesome-free',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'django_celery_results',
    'django_celery_beat',
    # LTI Toolbox
    'lti_toolbox',
    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',
    'django_select2',
    'pelp.apps.web',
    'pelp.apps.api',
    'pelp.apps.lti',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'pelp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path(__file__).resolve().parent / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pelp.wsgi.application'

# Channels
ASGI_APPLICATION = 'pelp.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv('REDIS_HOST', 'localhost'), int(os.getenv('REDIS_PORT', 6379)))],
        },
    },
}


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
if os.getenv('DB_ENGINE', 'sqlite3') == 'sqlite3':
    DATABASES = {
        'default': {
            #'ENGINE': 'django.db.backends.sqlite3',
            'ENGINE': 'django_prometheus.db.backends.sqlite3',
            'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            #'ENGINE': 'django.db.backends.mysql',
            'ENGINE': 'django_prometheus.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'pelp'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': get_secret('DB_PASSWORD'),
            'PORT': int(os.getenv('DB_PORT', 3306)),
            'HOST': os.getenv('DB_HOST')
        }
    }


AUTHENTICATION_BACKENDS = [
    "pelp.apps.lti.backend.LTIBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    Path(__file__).resolve().parent / 'locale',
]

LANGUAGES = [
    ('ca', _('Catalan')),
    ('es', _('Spanish')),
    ('en', _('English')),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, '..', '..', 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static')
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        #'rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 10,
}

# Required by DJango CKEditor (If disabled, all URLs used on front-end are not signed. DO NOT UNCOMMENT)
# AWS_QUERYSTRING_AUTH = False

# Your Amazon Web Services access key, as a string.
AWS_ACCESS_KEY_ID = get_secret('STORAGE_ACCESS_KEY')
# Your Amazon Web Services secret access key, as a string.
AWS_SECRET_ACCESS_KEY = get_secret('STORAGE_SECRET_KEY')
# Your Amazon Web Services storage bucket name, as a string.
AWS_STORAGE_BUCKET_NAME = get_secret('STORAGE_BUCKET_NAME')
# (optional: default is None) Name of the AWS S3 region to use (eg. eu-west-1)
AWS_S3_REGION_NAME = get_secret('STORAGE_REGION', 'eu-west-1')
# Custom S3 URL to use when connecting to S3, including scheme. Overrides AWS_S3_REGION_NAME and AWS_S3_USE_SSL.
AWS_S3_ENDPOINT_URL = get_secret('STORAGE_URL')
AWS_S3_SIGNATURE_VERSION = 's3v4'
# Disable SSL verification
if get_secret('STORAGE_SSL_VERIFY') is False:
    AWS_S3_VERIFY = False

# Get the public bucket name
AWS_S3_STORAGE_PUBLIC_BUCKET_NAME = get_secret('STORAGE_PUBLIC_BUCKET_NAME')
if AWS_ACCESS_KEY_ID is not None and AWS_SECRET_ACCESS_KEY is not None:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    if not DEBUG:
        STATICFILES_STORAGE = 'pelp.bucket.PublicS3Boto3Storage'
        STATIC_ROOT = '/'
    MEDIAFILES_STORAGE = 'pelp.bucket.PublicS3Boto3Storage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIAFILES_STORAGE = 'django.core.files.storage.FileSystemStorage'

CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_URL = 'redis://{}:{}'.format(os.getenv('REDIS_HOST', 'localhost'), int(os.getenv('REDIS_PORT', 6379)))
# CELERY_RESULT_BACKEND = 'redis://{}:{}'.format(os.getenv('REDIS_HOST', 'localhost'), int(os.getenv('REDIS_PORT', 6379)))
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseDatabaseScheduler'


EXECUTION_PATH = os.getenv('EXECUTION_PATH', '_executions')
DOCKER_MOUNT_ROOT_PATH = os.getenv('DOCKER_MOUNT_ROOT_PATH', EXECUTION_PATH)

MAX_PARALLEL_RUNS = int(os.getenv('MAX_PARALLEL_RUNS', 1))
DOCKER_API_URL = os.getenv('DOCKER_APY_URL', '')

# Output Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', None)
EMAIL_USE_TLS = True
EMAIL_FROM = os.getenv('EMAIL_FROM','pelp.inbox@gmail.com')

# Inbox IMAP Email configuration
IMAP_SERVER = os.getenv('IMAP_SERVER', None)
IMAP_USER = os.getenv('IMAP_USER', None)
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD', None)

# CK Editor options
CKEDITOR_UPLOAD_PATH = "/uploads/"
CKEDITOR_STORAGE_BACKEND = MEDIAFILES_STORAGE

CACHES = {
    "default": {
        #"BACKEND": "django_redis.cache.RedisCache",
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": 'redis://{}:{}'.format(os.getenv('REDIS_HOST', 'localhost'), int(os.getenv('REDIS_PORT', 6379))),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "pelp_cache_"
    }
}

SELECT2_CACHE_BACKEND = "default"

PROMETHEUS_METRICS_GW = os.getenv('PROMETHEUS_GW')


CORS_ALLOWED_ORIGINS = []
if len(os.getenv('CORS_ALLOWED_ORIGINS', '')) > 0:
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS').split(',')

CORS_ALLOW_CREDENTIALS = True
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_SCHEME', 'https')

# Canvas configuration
CANVAS_API_URL=get_secret('CANVAS_API_URL', 'https://aula.uoc.edu')
CANVAS_API_TOKEN=get_secret('CANVAS_API_TOKEN')


USE_CSP = False

#X_FRAME_OPTIONS = 'ALLOW-FROM https://aula.uoc.edu/'
#X_FRAME_OPTIONS = 'ALLOWALL'

if USE_CSP:
    # https://www.w3.org/TR/CSP/
    MIDDLEWARE += [
        'csp.middleware.CSPMiddleware',
    ]

    ALLOWED_CSP_SOURCES = tuple(ALLOWED_HOSTS) + tuple(["aula.uoc.edu", ])

    CSP_DEFAULT_SRC = ("'self'",) + ALLOWED_CSP_SOURCES

    #CSP_DEFAULT_SRC = ("'self'", ) + ALLOWED_CSP_SOURCES
    #CSP_DEFAULT_SRC = ("'none'",)
    #CSP_DEFAULT_SRC = ("'self'", "127.0.0.1:8000", "'unsafe-inline'", )
    #CSP_FRAME_SRC = ('http://127.0.0.1:8000',)
    #CSP_STYLE_SRC = ('*',)
    #CSP_SCRIPT_SRC = CSP_DEFAULT_SRC + ("'unsafe-inline'", )
    #CSP_FONT_SRC = CSP_DEFAULT_SRC + ("'unsafe-inline'", )
    #CSP_STYLE_SRC = CSP_DEFAULT_SRC + ("'unsafe-inline'", )
    #CSP_FONT_SRC = ('*',)
    #CSP_CONNECT_SRC = ('*',)
    #CSP_FRAME_ANCESTORS = CSP_DEFAULT_SRC

    # A tuple of URL prefixes. URLs beginning with any of these will not get the CSP headers. ('/admin')
    # CSP_EXCLUDE_URL_PREFIXES = ("http://localhost:63342/", )

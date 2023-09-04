from pathlib import Path
import os
import sys
# import dj_database_url

# for dev
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv

from django.contrib import messages
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

dotenv_file = find_dotenv(".env")
load_dotenv(dotenv_file)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

# DEBUG = os.getenv("DEBUG", "False")

if DEBUG is True:
    ALLOWED_HOSTS = ['64.227.46.124', 'localhost', 'app.writesome.ai', 'tools.writesome.ai']
else:
    ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,64.227.46.124,localhost").split(",")

# ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,64.227.46.124,localhost").split(",")

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    # Third-party APPS
    'crispy_forms',
    'crispy_bootstrap4',
    'django_user_agents',
    'django_gravatar',
    'mathfilters',

    # Local APPS
    'landing',
    'authorisation',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # third-party middlewares
    'django_user_agents.middleware.UserAgentMiddleware',
    'django_auto_logout.middleware.auto_logout',
]

ROOT_URLCONF = 'ukupendula.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'ukupendula.wsgi.app'

APP_NAME = 'Writesome'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#     }
# }

if DEVELOPMENT_MODE is True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'pendula',
            'USER': 'ukuser',
            'PASSWORD': 'gbHzwLohKxjf9dLFC7QqXJBY',
            'HOST': 'localhost',
            'PORT': '',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv("DATABASE_NAME"),
            'USER': os.getenv("DATABASE_USER"),
            'PASSWORD': os.getenv("DATABASE_PASS"),
            'HOST': os.getenv("DATABASE_HOST"),
            'PORT': '25060',
        }
    }
# elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
#     if os.getenv("DATABASE_URL", None) is None:
#         raise Exception("DATABASE_URL environment variable not defined")
#     DATABASES = {
#         "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
#     }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-gb'

FLAG_GB = 'dash/images/gb_flag.jpg'
FLAG_US = 'dash/images/us_flag.jpg'

TIME_ZONE = 'Africa/Johannesburg'

USE_I18N = True

USE_TZ = True

BASE_CURRENCY = 'ZAR'
BASE_CURR_SIGN = 'R'

LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'

AUTO_LOGOUT = {'IDLE_TIME': 7200}  # logout after 120 minutes of downtime(min * 60 sec)
# AUTO_LOGOUT = {'IDLE_TIME': 600}

BASE_API_URL = 'https://api.writesome.ai'
MAIN_API_KEY = os.getenv("MAIN_API_KEY")

OPENAI_API_KEYS = os.getenv("OPENAI_API_KEY")

DJANGORESIZED_DEFAULT_SIZE = [500, 500]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'PNG': ".png"}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

USE_SPACES = True
if USE_SPACES:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    AWS_STORAGE_BUCKET_NAME = 'writesome'
    AWS_S3_ENDPOINT_URL = 'https://writesome.syd1.digitaloceanspaces.com'
    AWS_S3_CUSTOM_DOMAIN = 'writesome.syd1.cdn.digitaloceanspaces.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    # only collect static without the writesome def
    # AWS_LOCATION = 'static'
    AWS_LOCATION = 'writesome/static'
    AWS_DEFAULT_ACL = 'public-read'

    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

    STATIC_URL = '{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
    STATIC_ROOT = 'static/'

    MEDIA_URL = '{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN, 'uploads')
    MEDIA_ROOT = '/uploads/'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
    MEDIA_URL = '/uploads/'

    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
TEMP = "{}/{}".format(MEDIA_ROOT, 'temp')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# django SMTP mail
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
EMAIL_REPLY_TO = os.getenv("EMAIL_REPLY_TO")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
# SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", False) == True
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", False) == True

PASSWORD_RESET_TIMEOUT = os.getenv("PASSWORD_RESET_TIMEOUT", 14400)

# CRISPY
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

#payfast.io
PAYFAST_SANDBOX_MODE = os.getenv("PAYFAST_SANDBOX_MODE", True) == False
# PAYFAST_SANDBOX_MODE = True
if PAYFAST_SANDBOX_MODE is True:
    PAYFAST_MERCHANT_ID = "10024789"
    PAYFAST_MERCHANT_KEY = "dtz5khr0cbz74"
    PAYFAST_PASS_PHRASE = "AnotidaL2022"
    PAYFAST_ACTION_URL = "https://sandbox.payfast.co.za/eng/process"
else:
    PAYFAST_MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID")
    PAYFAST_MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY")
    PAYFAST_PASS_PHRASE = os.getenv("PAYFAST_PASS_PHRASE")
    PAYFAST_ACTION_URL = os.getenv("PAYFAST_ACTION_URL")

PAYFAST_URL_BASE = os.getenv("PAYFAST_URL_BASE")

FREE_SUBSCR_PACKAGE = os.getenv("FREE_SUBSCR_PACKAGE", "04955d2545f0")

CF_SITE_KEY = os.getenv("CF_SITE_KEY")
CF_PRIVATE_KEY = os.getenv("CF_PRIVATE_KEY")

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

TOS_URL = '#'
CONTACT_URL = 'https://writesome.ai/contact-us/'
OPT_OUT_URL = '#'

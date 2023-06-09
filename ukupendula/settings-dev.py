from pathlib import Path
import os
import sys
import dj_database_url

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

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

if DEBUG is True:
    ALLOWED_HOSTS = ['138.68.155.44', 'localhost', 'app.writesome.ai']
    dotenv_file = find_dotenv(".env")
    load_dotenv(dotenv_file)
else:
    ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "True") == "True"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party APPS
    'crispy_forms',
    'crispy_bootstrap4',
    'django_user_agents',
    'django_gravatar',

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
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
    }


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

TIME_ZONE = 'Africa/Johannesburg'

USE_I18N = True

USE_TZ = True

BASE_CURRENCY = 'ZAR'
BASE_CURR_SIGN = 'R'


LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'

OPENAI_API_KEYS = os.getenv("OPENAI_API_KEY")
MAILER_API_URL = os.getenv("MAILER_API_URL", "https://api.ukudev.co.za")
MAILER_API_KEY = os.getenv("MAILER_API_KEY", "UKU-MakNzlhMjFlYjlmZGNlY2MzY2UxMjJhODdjN2U2")
API_KEY_OWNER = os.getenv("API_KEY_OWNER", "TTB0002")

DJANGORESIZED_DEFAULT_SIZE = [500, 500]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'PNG': ".png"}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/uploads/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Emailing settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
EMAIL_HOST = 'branding.writesome.ai'
EMAIL_FROM = 'no-reply@writesome.ai'
EMAIL_HOST_USER = 'no-reply@writesome.ai'
EMAIL_HOST_PASSWORD = 'DGA-xkx8tcj7jzb4ycf'
EMAIL_PORT = 587
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False


PASSWORD_RESET_TIMEOUT = 14400

# CRISPY
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

#payfast.io
PAYFAST_MERCHANT_ID = '10024789'
PAYFAST_MERCHANT_KEY = 'dtz5khr0cbz74'
PAYFAST_URL_BASE = ''

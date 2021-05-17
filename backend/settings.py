"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/

Data dump:
python3 manage.py dumpdata --exclude contenttypes --exclude auth.permission > data/db.json
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$!lxh62t%%9l(jw9fsn-my-fhe18$2+4n1$*n**k6w#bzv$j1f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ["product-factory-frontend-next.herokuapp.com"]
ALLOWED_HOSTS = ["*"]

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # 3rd party apps
    'graphene_django',
    'corsheaders',
    'django_filters',
    'notifications',
    'treebeard',
    'polymorphic',

    # local apps
    'work',
    'talent',
    'commercial',
    'matching',
    'api',
    'git',
    'comments',
    'license',
    'images',
    'users',
    'ideas_bugs',
]

GRAPHENE = {
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": True,
    "RELAY_CONNECTION_MAX_LIMIT": 100
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'ou_db'),
        'USER': os.environ.get('POSTGRES_USER', 'dev'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'mypass'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': os.environ.get('POSTGRES_POST', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(BASE_DIR / "backend" / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

SITE_ID = 1

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')  # abs path on server
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.yourserver.com'
# EMAIL_PORT = '<your-server-port>'
EMAIL_HOST = 'support@em9640.openunited.com'
# EMAIL_HOST_PASSWORD = 'your-email account-password'
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False

CORS_ORIGIN_ALLOW_ALL = True

FRONT_END_SERVER = os.environ.get('FRONT_END_SERVER', '')

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:8080',
    'https://open-united-backend.herokuapp.com',
    'https://open-united.herokuapp.com',
    'https://product-factory-frontend-next.herokuapp.com',
]

CSRF_TRUSTED_ORIGINS = [
    'open-united.herokuapp.com',
    'product-factory-frontend-next.herokuapp.com',
]

CORS_ALLOW_CREDENTIALS = True

# SESSION_COOKIE_SECURE = True
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_USE_SESSIONS = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = False

# AuthMachine options
AUTHMACHINE_URL = os.environ.get('AUTHMACHINE_URL', '')
AUTHMACHINE_CLIENT_ID = os.environ.get('AUTHMACHINE_CLIENT_ID', '')
AUTHMACHINE_CLIENT_SECRET = os.environ.get('AUTHMACHINE_CLIENT_SECRET', '')
AUTHMACHINE_API_TOKEN = os.environ.get('AUTHMACHINE_API_TOKEN', '')
AUTHMACHINE_SCOPE = 'openid email profile'

UID_MAX_LENGTH = 191

try:
    from .local_settings import *
except ImportError:
    pass

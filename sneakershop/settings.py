"""Postavke za Django projekt sneakershop."""

import os

from pathlib import Path
import dj_database_url

# Putanje unutar projekta (npr. BASE_DIR / 'subdir').
BASE_DIR = Path(__file__).resolve().parent.parent



# Brze postavke za razvoj (nisu za produkciju).
# Vidi: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SIGURNOSNO: tajni ključ za produkciju mora ostati tajan!
# U produkciji OBAVEZNO postavi DJANGO_SECRET_KEY.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SIGURNOSNO: nemoj imati DEBUG uključen u produkciji!
# Lokalno: DJANGO_DEBUG=1 (default), produkcija: DJANGO_DEBUG=0
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'

if not SECRET_KEY:
    if DEBUG:
        # Samo za lokalni razvoj
        SECRET_KEY = 'django-insecure-dev-key-change-me'
    else:
        raise RuntimeError('DJANGO_SECRET_KEY nije postavljen (a DEBUG je isključen).')

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'testserver',
]


# Minimalne sigurnosne postavke za produkciju.
# Ne diramo lokalni razvoj (DEBUG=True) da sve radi bez HTTPS-a.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Dovoljno za "osnovne" provjere; povećaj kad si siguran da je HTTPS uvijek upaljen.
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '3600'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# Definicija aplikacija

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sneakershop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sneakershop.wsgi.application'


# Baza podataka
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASE_URL = os.environ.get('SUPABASE_DB_URL') or os.environ.get('DATABASE_URL')
DATABASE_SSLMODE = os.environ.get('DATABASE_SSLMODE', 'require').lower()
SSL_REQUIRED = DATABASE_SSLMODE in {'require', 'verify-full', 'true', '1'}

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=SSL_REQUIRED,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Validacija lozinke
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internacionalizacija
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'hr'

TIME_ZONE = 'Europe/Zagreb'

USE_I18N = True

USE_TZ = True


# Statičke datoteke (CSS, JavaScript, slike)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Dodatni direktorij za lokalne statičke datoteke
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default tip primarnog ključa
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

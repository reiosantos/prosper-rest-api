
"""
Django settings for prosper project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from config.prosper import HOSTS, DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT, COMPANY_EMAIL

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MAIN_HOME_DIR = os.path.join(BASE_DIR, 'home')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(3r#690b&r#!2po+m5n_x(wys7-(z8b+&yq(q2y*l4w$yk5-^%'

DEBUG = True

ALLOWED_HOSTS = HOSTS

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'documents',
    'finance',
    'home',
    'message',
    'others',
    'settings',
    'crispy_forms',
    'django_excel',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

DEFAULT_FROM_EMAIL = COMPANY_EMAIL

SERVER_EMAIL = COMPANY_EMAIL

MEDIA_ROOT = os.path.join(MAIN_HOME_DIR, 'uploads')

REPORT_ROOT = os.path.join(MAIN_HOME_DIR, 'reports')

MEDIA_URL = '/uploads/'

LOGIN_URL = 'login_user'

LOGOUT_REDIRECT_URL = 'login_user'

LOGIN_REDIRECT_URL = 'home_page'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o777

FILE_UPLOAD_PERMISSIONS = 0o777

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(MAIN_HOME_DIR, 'static'),
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(MAIN_HOME_DIR, 'templates'),
            os.path.join(BASE_DIR, 'documents/templates'),
            os.path.join(BASE_DIR, 'finance/templates'),
            os.path.join(BASE_DIR, 'home/templates'),
            os.path.join(BASE_DIR, 'message/templates'),
            os.path.join(BASE_DIR, 'others/templates'),
            os.path.join(BASE_DIR, 'settings/templates'),
            os.path.join(BASE_DIR, 'users/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.site_vars',
            ],
        },
    },
]

AUTH_USER_MODEL = 'users.User'

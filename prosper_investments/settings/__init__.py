"""
Django settings for prosper project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
	'grappelli',  # disabled for now
	'django.apps',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'rest_framework',

	'prosper_investments.apps.venue',
	'prosper_investments.apps.user',
	'prosper_investments.apps.account',
	'prosper_investments.apps.common',
	'prosper_investments.apps.email',
	'prosper_investments.apps.oauth',
	'prosper_investments.apps.permission',
	'prosper_investments.apps.terminology',

	'django_filters',
	'django_countries',
	'import_export',
	'corsheaders',
	'rest_framework_swagger',
	'crispy_forms'
]

SITE_ID = 1

URL_PREFIX = 'api'

AUTH_USER_MODEL = 'venue.User'

PASSWORD_HASHERS = [
	"django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

# The default customer support email address
DEFAULT_SUPPORT_EMAIL = 'support@prosperinv.com'

ADMIN_EMAIL = 'admin@prosperinv.com'
SERVER_EMAIL = 'no-reply@prosperinv.com'
DEFAULT_FROM_EMAIL = 'no-reply@prosperinv.com'

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'prosper_investments.apps.venue.middleware.VenueMiddleware',
	'prosper_investments.apps.venue.middleware.RestrictStaffToAdminMiddleware'
]

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'HOST': os.getenv('DB_HOST', ''),
		'PORT': os.getenv('DB_PORT', '3306'),
		'NAME': os.getenv('DB_NAME', ''),
		'USER': os.getenv('DB_USERNAME', ''),
		'PASSWORD': os.getenv('DB_PASSWORD', ''),
		'OPTIONS': {
			'sql_mode': 'STRICT_TRANS_TABLES',
		}
	},
}

# Languages available for translation; used by locale middleware.
LANGUAGES = [
	('en-gb', 'British English'),
	('en-us', 'American English'),
	('en-ca', 'Canadian English'),
	('fr', 'French'),
	('es', 'Spanish'),
]

AUTHENTICATION_BACKENDS = [
	'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'prosper_investments.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [
			os.path.join(BASE_DIR, 'templates')
		],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.contrib.auth.context_processors.auth',
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.template.context_processors.i18n',
				'django.template.context_processors.media',
				'django.template.context_processors.static',
				'django.template.context_processors.tz',
				'django.contrib.messages.context_processors.messages',
				'prosper_investments.apps.common.tpl_context.site_vars',
			],
		},
	},
]

REST_FRAMEWORK = {
	'DEFAULT_PAGINATION_CLASS': None,
	'DEFAULT_RENDERER_CLASSES': (
		'prosper_investments.apps.common.psp_camel_case.render.CamelCaseJSONRenderer',),
	'DEFAULT_PARSER_CLASSES': (
		'prosper_investments.apps.common.psp_camel_case.parser.CamelCaseJSONParser',
		'rest_framework.parsers.MultiPartParser',
		'rest_framework.parsers.FormParser',
	),
	'DEFAULT_PERMISSION_CLASSES': (
		'rest_framework.permissions.IsAuthenticated',
	),
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'prosper_investments.apps.user.authentication.JSONWebTokenAuthenticationPost',
	),
	'DEFAULT_FILTER_BACKENDS': (
		'django_filters.rest_framework.DjangoFilterBackend',
	),
	'EXCEPTION_HANDLER': 'prosper_investments.apps.common.exception_handler',
	'DEFAULT_THROTTLE_CLASSES': [
		'rest_framework.throttling.AnonRateThrottle',
		'rest_framework.throttling.UserRateThrottle'
	],
	'DEFAULT_THROTTLE_RATES': {
		'anon': '20/minute',
		'user': '400/minute'
	}
}

JWT_AUTH = {
	'JWT_VERIFY_EXPIRATION': False,
	'JWT_RESPONSE_PAYLOAD_HANDLER':
		'prosper_investments.apps.user.utils.psp_jwt_response_payload_handler',
	'JWT_PAYLOAD_HANDLER': 'prosper_investments.apps.user.utils.psp_jwt_payload_handler'
}

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = [
	'x-requested-with',
	'content-type',
	'accept',
	'origin',
	'authorization',
	'x-csrftoken',
	'user-agent',
	'accept-encoding',
	'if-modified-since',
]

WSGI_APPLICATION = 'prosper_investments.wsgi.application'

SECRET_KEY = '(3r#690b&r#!2po+m5n_x(wys7-(z8b+&yq(q2y*l4w$yk5-^%'

DEBUG = os.getenv('DEBUG', False)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'

PSP_DASHBOARD_URL = 'https://stg-%s.prosperinv.com/dashboard-'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = f'/{URL_PREFIX}/static/' if URL_PREFIX else '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# Additional locations of static files
STATICFILES_DIRS = [
	os.path.join(BASE_DIR, 'public'),
]

MEDIA_URL = f'/{URL_PREFIX}/media/' if URL_PREFIX else '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

PSP_BASE_URL = os.getenv('BASE_URL', 'http://local.prosperinv.com')
PSP_DASHBOARD_URL = f'{PSP_BASE_URL}dashboard/'

FIXTURE_DIRS = [
	os.path.join(BASE_DIR, 'fixtures'),
	os.path.join(BASE_DIR, 'fixtures/test'),
]

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = 587

FILE_UPLOAD_HANDLERS = ['django.core.files.uploadhandler.TemporaryFileUploadHandler']

FILE_UPLOAD_MAX_ATTACH_NUM = 10

# in bytes, see https://docs.djangoproject.com/en/1.8/ref/files/file/#django.core.files.File.size
FILE_UPLOAD_MAX_SIZE = 10 * 1024 * 1024 # 10MB

FILE_UPLOAD_TYPES = [
	'application/pdf', 'image/png', 'image/jpeg', 'application/msword',
	'application/vnd.ms-excel', 'application/vnd.ms-office'
]

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'simple': {
			'format': '[%(asctime)s] %(levelname)s %(message)s',
			'datefmt': '%Y-%m-%d %H:%M:%S'
		},
		'verbose': {
			'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
			'datefmt': '%Y-%m-%d %H:%M:%S'
		},
		'django.server': {
			'()': 'django.utils.log.ServerFormatter',
			'format': '[%(server_time)s] %(message)s',
		}
	},
	'handlers': {
		'console': {
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			'formatter': 'simple',
		},
		'file': {
			'level': 'DEBUG',
			'class': 'logging.handlers.TimedRotatingFileHandler',
			'when': 'midnight',
			'filename': '/var/log/prosper_investments/prosper_investments.log',
			'formatter': 'verbose',
		},
		'logstash': {
			'level': 'DEBUG',
			'class': 'logstash.TCPLogstashHandler',
			'host': os.getenv('LOGSTASH_HOST', 'localhost'),
			'port': os.getenv('LOGSTASH_PORT', '5959'),  # Default value: 5959
			'version': 1,
			'message_type': 'django',
			# 'type' field in logstash message. Default value: 'logstash'.
			'fqdn': False,  # Fully qualified domain name. Default value: false.
			'tags': ['django.request'],  # list of tags. Default: None.
		},
		'request_handler': {
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': '/var/log/prosper_investments/requests.log',
			'maxBytes': 1024 * 1024 * 5,  # 5MB
			'backupCount': 5,
			'formatter': 'simple'
		},
		'django.server': {
			'level': 'INFO',
			'class': 'logging.StreamHandler',
			'formatter': 'django.server',
		},
	},
	'loggers': {
		'prosper_investments': {
			'handlers': ['console', 'file'],
			'level': 'DEBUG',
			'propagate': True,
		},
		'django.request': {
			'handlers': ['request_handler'],
			'level': 'DEBUG',
			'propagate': False
		},
		'django.server': {
			'handlers': ['django.server'],
			'level': 'INFO',
			'propagate': False,
		}
	}
}

PASSWORD_RESET_TIMEOUT_DAYS = 1

SSL_ENABLED = True

SWAGGER_SETTINGS = {
	'api_version': '1.0',
	'info': {
		'description':
			'This is the official API documentation for the Prosper Investments management software',
		'title': 'Prosper Investments API Documentation'
	},
	'api_path': '/api/',
	'base_path': 'local.prosperinv.com/api/docs'
}

GRAPPELLI_ADMIN_TITLE = 'Prosper Investments'

# CELERY STUFF
RMQ = {
	'db': {
		'ROUTING_KEY': 'rest_api.db.%ss.%ss',
	},
	'schedule': {
		'ROUTING_KEY': 'rest_api.schedule.remind',
	},
	'QUEUE_NAME': 'psp.q.rest_api',
	'MASTER_EXCHANGE': 'psp.ex',
	'TEST_PREFIX': 'test_',
	'HOST': os.getenv('RABBITMQ_HOST', 'localhost'),
	'admin_user': os.getenv('RABBITMQ_DEFAULT_USER', ''),
	'admin_pass': os.getenv('RABBITMQ_DEFAULT_PASS', ''),
}

BROKER_URL = 'amqp://%s:%s@%s/' % (
	os.getenv('RABBITMQ_DEFAULT_USER', ''),
	os.getenv('RABBITMQ_DEFAULT_PASS', ''),
	os.getenv('RABBITMQ_HOST', 'localhost')
)
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = BROKER_URL

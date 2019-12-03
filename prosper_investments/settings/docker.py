# noinspection PyUnresolvedReferences
import os

from prosper_investments.settings import *

DB_USER = os.environ.get('DB_USERNAME', 'prosper_investments')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'prosper_investments')
DB_NAME = os.environ.get('DB_NAME', 'prosper_investments')
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_PORT = os.environ.get('DB_PORT', '3306')

ALLOWED_HOSTS = ['*']

DATABASES['default'].update({
	'USER': DB_USER,
	'PASSWORD': DB_PASSWORD,
	'NAME': DB_NAME,
	'HOST': DB_HOST,
	'PORT': DB_PORT,
})

PSP_DASHBOARD_URL = 'http://local.prosperinv.com/dashboard/'
PSP_REST_API_BASE_URL = 'http://local.prosperinv.com/api/'

SSL_ENABLED = False

ELASTIC_APM['SERVICE_NAME'] = 'rest_api_docker'
ELASTIC_APM['DEBUG'] = True

INSTALLED_APPS += (
	'silk',
)

MIDDLEWARE = ('silk.middleware.SilkyMiddleware',) + MIDDLEWARE

SILKY_META = True
SILKY_PYTHON_PROFILER = True

SILKY_DYNAMIC_PROFILING = []

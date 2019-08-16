# noinspection PyUnresolvedReferences
from prosper_investments.settings import *

ALLOWED_HOSTS = ['*']

SERVER_EMAIL = 'stg-no-reply@prosperinv.com'

DEFAULT_FROM_EMAIL = 'stg-info@prosperinv.com'

PSP_DASHBOARD_URL = 'https://stg-%s.prosperinv.com/dashboard/'

PSP_REST_API_BASE_URL = 'https://stg-api.prosperinv.com/api/'

ELASTIC_APM['SERVICE_NAME'] = 'rest_api_staging'

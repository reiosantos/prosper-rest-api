# noinspection PyUnresolvedReferences
from prosper_investments.settings import *

ADMINS = (
    ('Reio Santos', 'santos@prosperinv.com'),
)

ALLOWED_HOSTS = ['*']

SERVER_EMAIL = 'no-reply@prosperinv.com'
DEFAULT_FROM_EMAIL = 'info@prosperinv.com'

# IMPORTANT On a production server, ensure that a unique key is generated
SECRET_KEY = ';i}xOSFlh2v+y-SsXl!)JnJ/7Kb(tOJH7J1=~z6c_{eSr,S;{l'

PSP_DASHBOARD_URL = 'https://%s.prosperinv.com/dashboard/'

PSP_REST_API_BASE_URL = 'https://ecs-api.prosperinv.com/api/'

ELASTIC_APM['SERVICE_NAME'] = 'rest_api_production'

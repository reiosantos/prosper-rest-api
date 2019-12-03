# depends
"""
    django==1.11.6
    django-crispy-forms==1.6.1
    python-pytz , a timezone module
    pillow
    python-magic==0.4.13 a python module for file type and file mime validation
    django-excel, for uploading and dealing with excel files( also pyexcel-xls, pyexce-xlsx)

    populate timezone info in mysql database.. use the following commands on the server
    -> mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql
    -> mysql -u root -p -e "flush tables;" mysql
    -> sudo service mysql restart
"""
# Details about the company
import os

from dotenv import load_dotenv

load_dotenv()

COMPANY_NAME = 'Prosper Investments'
COMPANY_TITLE = 'prosper investments company'
COMPANY_CONTACT = os.getenv('COMPANY_CONTACT')
COMPANY_EMAIL = os.getenv('COMPANY_EMAIL')

# database
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USERNAME')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = ''

# email hosting configurations
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = COMPANY_EMAIL
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

HOSTS = ['localhost', '127.0.0.1', '127.0.1.1', '192.168.43.210']

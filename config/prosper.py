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
COMPANY_NAME = 'Prosper Investments'
COMPANY_TITLE = 'prosper investments company'
COMPANY_CONTACT = '0779104144'
COMPANY_EMAIL = 'ronireiosantos@gmail.com'

# database
DB_NAME = 'prosper'
DB_USER = 'root'
DB_PASS = 'santos'
DB_HOST = 'localhost'
DB_PORT = ''

# email hosting configurations
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = COMPANY_EMAIL
EMAIL_HOST_PASSWORD = 'ronald507'
EMAIL_PORT = 587

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

HOSTS = ['localhost', '127.0.0.1', '127.0.1.1', '192.168.43.210']

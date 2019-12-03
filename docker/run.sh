#!/bin/bash

if [[ $CELERY == 'worker' ]]; then
	celery -A prosper_investments.celery worker -E

elif [[ $ENV == 'local' ]]; then
	#statements
	echo "ENV LOCAL -------------------"
	python manage.py makemigrations
	python manage.py migrate --noinput
	python manage.py runserver 0.0.0.0:8000
else
	cp /usr/src/app/nginx.conf /etc/nginx/conf.d/default.conf
	cp /usr/src/app/supervisor.conf /etc/supervisor/conf.d/
	supervisord -n
fi

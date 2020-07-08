#!/bin/bash

if [[ $CELERY == 'worker' ]]; then
	supervisord -n -c /usr/src/app/supervisor.celery.worker.conf

elif [[ $CELERY == 'beat' ]]; then
	supervisord -n -c /usr/src/app/supervisor.celery.beat.conf

else
	if [[ $ENV == 'local' ]]; then
		#statements
		echo "ENV LOCAL -------------------"
		python manage.py migrate --noinput
		python manage.py loaddata prosper_investments/fixtures/*.json
		python manage.py runserver 0.0.0.0:8000
	else
		cp /usr/src/app/nginx.conf /etc/nginx/conf.d/default.conf
		cp /usr/src/app/supervisor.conf /etc/supervisor/conf.d/
		supervisord -n
	fi
fi

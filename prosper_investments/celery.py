import os
# set the default Django settings module for the 'celery' program.
from datetime import timedelta

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prosper_investments.settings')

from django.conf import settings  # noqa

app = Celery('prosper_investments')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.CELERYBEAT_SCHEDULE = {

}

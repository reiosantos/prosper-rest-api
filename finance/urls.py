
from django.contrib.auth.decorators import login_required

from django.conf.urls import url

from finance.views import investments, investments_update, contributions, loans, statements, loans_update

urlpatterns = [

    url(r'^investments/$', login_required(investments), name='investments'),
    url(r'^investments/update/(?:(?P<ids>[0-9]+))?$', login_required(investments_update),
        name='investments_update'),
    url(r'^contributions/$', login_required(contributions), name='contributions'),
    url(r'^loans/$', login_required(loans), name='loans'),
    url(r'^loans/update/(?:(?P<ids>[0-9]+))?$', login_required(loans_update),
        name='loans_update'),
    url(r'^statements/$', login_required(statements), name='statements'),

]
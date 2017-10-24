
from django.contrib.auth.decorators import login_required

from django.conf.urls import url

from home.views import index, no_script

urlpatterns = [

    url(r'^$', login_required(index), name='home_page'),
    url(r'^no_script/error/cant-load/page/$', login_required(no_script), name='noscript_page'),

]
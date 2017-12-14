
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from home.views import index, no_script, PrintFunction

urlpatterns = [

    url(r'^$', login_required(index), name='home_page'),
    url(r'^no_script/error/cant-load/page/$', login_required(no_script), name='noscript_page'),
    url(r'^print/(?:(?P<what>\w+))?/$', login_required(PrintFunction.as_view()), name='print_function'),

]
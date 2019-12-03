
from django.contrib.auth.decorators import login_required

from django.conf.urls import url

from others.views import ideas, market

urlpatterns = [

    url(r'^others/ideas/$', login_required(ideas), name='ideas'),
    url(r'^others/market/$', login_required(market), name='market'),

]
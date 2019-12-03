
from django.contrib.auth.decorators import login_required

from django.conf.urls import url

from message.views import compose, inbox, sent

urlpatterns = [

    url(r'^compose/$', login_required(compose), name='compose'),
    url(r'^inbox/$', login_required(inbox), name='inbox'),
    url(r'^sent/$', login_required(sent), name='sent'),

]

from django.contrib.auth.decorators import login_required

from django.conf.urls import url

from documents.views import upload, view_all

urlpatterns = [

    url(r'^upload/$', login_required(upload), name='upload'),
    url(r'^all/$', login_required(view_all), name='view_all'),

]
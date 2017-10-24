
from django.contrib.auth.decorators import login_required

from django.conf.urls import url

from settings.views import schedule_meeting, all_meetings, new_event, all_events

urlpatterns = [

    url(r'^meetings/add/$', login_required(schedule_meeting), name='schedule_meeting'),
    url(r'^meetings/$', login_required(all_meetings), name='all_meetings'),
    url(r'^events/add/$', login_required(new_event), name='new_event'),
    url(r'^events/$', login_required(all_events), name='all_events'),

]
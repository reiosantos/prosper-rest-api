
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from django.conf.urls import url

from users.views import login_user, logout_user, profile, add_user, manage_users, ajax, profile_graph

urlpatterns = [
    url(r'^login/$', login_user, name='login_user'),
    url(r'^logout/$', login_required(logout_user), name='logout_user'),
    url(r'^password/change/$', login_required(auth_views.PasswordChangeView.as_view()), name='password_change'),
    url(r'^password/change/done$', login_required(auth_views.PasswordChangeDoneView.as_view()),
        name='password_change_done'),
    url(r'^password/reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    url(r'^profile/$', login_required(profile), name='profile_page'),
    url(r'^profile/graph/$', login_required(profile_graph), name='profile_graph'),
    url(r'^add/$', login_required(add_user), name='add_user'),
    url(r'^manage/$', login_required(manage_users), name='manage_users'),
    url(r'^manage/ajax/$', login_required(ajax), name='manage_ajax_user'),
]

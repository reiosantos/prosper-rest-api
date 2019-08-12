"""voyage_control URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
import django
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import re_path, path
from djoser import views as djoser_views
from djoser.views import SetPasswordView
from rest_framework_jwt import views
from rest_framework_swagger.views import get_swagger_view

from prosper_investments.apps.common.handlers import (
	psp_page_not_found, psp_bad_request, psp_permission_denied, psp_server_error)
from prosper_investments.apps.common.views import ApiKeyVerify, HealthCheckView
from prosper_investments.apps.user import views as userviews

schema_view = get_swagger_view(title='PSP Rest API')

urlpatterns = [
	path('admin/', admin.site.urls),
	path('auth/', include('rest_framework.urls', namespace='rest_framework')),
	path('jwt/login/', views.obtain_jwt_token),
	path('jwt/verify/', views.verify_jwt_token),
	path('apikey/verify/', ApiKeyVerify.as_view({'post': 'post'}), name='apikey-verify'),
	path('health/', HealthCheckView.as_view({'get': 'get'}), name='health_check'),
	path('docs/', schema_view),
	path('user/', include('prosper_investments.apps.user.urls', namespace='user')),
	path('password/reset/', userviews.PasswordResetView.as_view(), name='password_reset'),
	path('password/reset-form/', userviews.password_reset, name='password_reset_form'),
	path(
		'password/reset/confirm/', djoser_views.PasswordResetConfirmView.as_view(),
		name='password_reset_confirm'),
	path(
		'password/reset/done/', auth_views.PasswordResetCompleteView.as_view(),
		name='password_reset_complete'),
	re_path(
		r'password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
		auth_views.PasswordResetConfirmView.as_view(), name='password_reset_token'),
	path('password/set/', SetPasswordView.as_view(), name='password_set'),
	path('venue/', include('prosper_investments.apps.venue.urls', namespace='venue')),
	path('oauth/', include('prosper_investments.apps.oauth.urls', namespace='oauth')),
	path(
		'permission/', include('prosper_investments.apps.permission.urls', namespace='permission')),
	path(
		'terminology/',
		include('prosper_investments.apps.terminology.urls', namespace='terminology')),
	path('email/', include('prosper_investments.apps.email.urls', namespace='email')),
]

# @TODO in production, serve files differently
urlpatterns += [
	# static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
	re_path(
		r'^media/(?P<path>.*)$', django.conf.urls.static.serve,
		{'document_root': settings.MEDIA_ROOT})
]

handler400 = psp_bad_request
handler404 = psp_page_not_found
handler403 = psp_permission_denied
handler500 = psp_server_error

import logging

# Avoid shadowing the login() and logout() views below.
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from djoser.views import PasswordResetView as DjoserPasswordResetView
from rest_framework import response, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, GenericAPIView, \
	CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from prosper_investments.apps.email.utils import WelcomeEmail, PasswordResetEmail, site_url, \
	VerifyUserEmail
from prosper_investments.apps.permission.permissions import ManagementPermissions
from prosper_investments.apps.permission.serializers import ContributionPermissionSerializer
from prosper_investments.apps.user import serializers
from prosper_investments.apps.user.models import DashboardSection, VenueViewerType
from prosper_investments.apps.user.pagination import UserInOrganisationPagination
from prosper_investments.apps.user.utils import (
	users_venue_permissions, user_exists_as_email, user_exists_as_mobile, filter_order_by)
from prosper_investments.apps.venue.models import User

log = logging.getLogger('prosper_investments')


class CurrentUserView(RetrieveAPIView):
	"""
	Info about the current Company User.
	"""
	serializer_class = serializers.UserSerializer

	def get_object(self):
		return self.request.user


class EditProfileView(UpdateAPIView, GenericAPIView):
	"""
    Edit the currently logged in user's profile.
    """
	serializer_class = serializers.EditUserSerializer

	def post(self, request):
		return self.partial_update(request)

	def get_object(self):
		return self.request.user


class CreateUserView(CreateAPIView):
	"""
	Create a User.
	"""
	permission_classes = (AllowAny,)
	serializer_class = serializers.CreateUserSerializer

	def get_serializer_context(self):
		return {'is_active': False}

	def perform_create(self, serializer):
		serializer.save()
		user = serializer.instance
		uri = 'dashboard/welcome?verifyEmail={0}'.format(user.id)
		link = site_url(self.request, uri)
		context = {
			'request': self.request,
			'to': user.email,
			'link': link
		}
		VerifyUserEmail(user, context).send()


class ActivateUserView(UpdateAPIView):
	"""
	Activate a User.
	"""
	permission_classes = (AllowAny,)
	serializer_class = serializers.ActivateUserSerializer

	def perform_update(self, serializer):
		serializer.save()
		user = serializer.instance
		context = {'request': self.request}
		email = WelcomeEmail(user, context=context)
		email.send()

	def get_object(self):
		user_id = self.request.data.get('user_id')
		if user_id:
			return User.objects.get(pk=user_id)


class UserVenuePermissionsView(APIView):
	"""
	Get list of permissions for user and venue.
	params:
	- venue (from url parameter)
	- user (from authentication header)
	"""
	permission_classes = (IsAuthenticated,)

	serializer_class = ContributionPermissionSerializer

	def get(self, request):
		if not request.venue:
			raise ValidationError('No venue specified')

		user_permissions = users_venue_permissions(request.venue, request.user)

		return Response(user_permissions)


class UserExistView(APIView):
	permission_classes = (AllowAny,)

	def get(self, request):
		if self.request.GET.get('mobile', False):
			return Response(user_exists_as_mobile(self.request.GET.get('mobile')))
		elif self.request.GET.get('email', False):
			return Response(user_exists_as_email(self.request.GET.get('email')))
		else:
			return Response(False)


class DashboardSectionsView(ListAPIView):
	permission_classes = (ManagementPermissions,)

	serializer_class = serializers.DashboardSectionSerializer

	def get_queryset(self):
		return DashboardSection.objects.all()


class VenueViewerTypesViewSet(ModelViewSet):
	permission_classes = (ManagementPermissions,)

	serializer_class = serializers.VenueViewerTypeSerializer

	def get_queryset(self):
		return VenueViewerType.objects.filter(venue=self.request.venue) \
			.prefetch_related('permissions', 'sections')


class UsersInOrganisationDefaultPermissionViewSet(ModelViewSet):
	permission_classes = (IsAuthenticated,)

	serializer_class = serializers.UserInOrganisationSerializer
	pagination_class = UserInOrganisationPagination

	def get_queryset(self):
		queryset = User.objects.filter(venue=self.request.venue)

		search = self.request.query_params.get('search', None)
		if search:
			queryset = queryset.filter(
				Q(email__icontains=search) |
				Q(profile__first_name__icontains=search) |
				Q(profile__last_name__icontains=search)
			)

		return queryset

	def perform_destroy(self, instance):
		"""
		'Deleting' a user in this context means removing all of their
		'viewer-types' for the venue in question.
		"""
		instance.viewer_types.filter(venue=self.request.venue).clear()


class UsersInOrganisationViewSet(ModelViewSet):
	permission_classes = (ManagementPermissions,)

	serializer_class = serializers.UserInOrganisationSerializer
	pagination_class = UserInOrganisationPagination

	def get_queryset(self):

		search = self.request.query_params.get('search', None)
		blank_role = self.request.query_params.get('blank', None)
		roles = self.request.GET.getlist('roles', None)

		queryset = User.objects.filter(venue=self.request.venue)

		if blank_role:
			queryset = queryset.filter().exclude(viewer_types__venue__id=self.request.venue.id) \
				.distinct()

		if roles:
			queryset = queryset.filter(viewer_types__in=roles)

		if search:
			queryset = queryset.filter(
				Q(email__icontains=search) |
				Q(company__name__icontains=search) |
				Q(profile__first_name__icontains=search) |
				Q(profile__last_name__icontains=search)
			)

		queryset = filter_order_by(self.request, queryset)

		return queryset

	def perform_destroy(self, instance):
		"""
        'Deleting' a user in this context means removing all of their
        'viewer-types' for the venue in question.
        """
		instance.viewer_types.filter(venue=self.request.venue).clear()


class UsersInOrganisationShortViewSet(ReadOnlyModelViewSet):
	permission_classes = (ManagementPermissions,)
	serializer_class = serializers.UserInOrganisationShortSerializer

	def get_queryset(self):
		queryset = User.objects.filter(venue=self.request.venue)

		search = self.request.query_params.get('search', None)
		if search:
			queryset = queryset.filter(
				Q(email__icontains=search) |
				Q(profile__first_name__icontains=search) |
				Q(profile__last_name__icontains=search)
			)

		return queryset

	def perform_destroy(self, instance):
		"""
        'Deleting' a user in this context means removing all of their
        'viewer-types' for the venue in question.
        """
		instance.viewer_types.filter(venue=self.request.venue).clear()


class PasswordResetView(DjoserPasswordResetView):
	"""
	A view which sends a templated email to the posted email address with a password reset link
	"""

	def action(self, serializer):
		users = self.get_users(serializer.data['email'])

		# send 404 if no users found
		if users:
			for user in users:
				# noinspection PyUnresolvedReferences
				self.send_email(**self.get_send_email_kwargs(user))
			return response.Response(status=status.HTTP_200_OK)
		else:
			return response.Response(status=status.HTTP_404_NOT_FOUND)

	def get_users(self, email):
		# only active users
		active_users = User.objects.filter(email__iexact=email, is_active=True)
		return active_users

	def send_email(self, to_email, from_email, context):
		link = site_url(self.request, context['url'])
		user = User.objects.get(email=to_email)
		context.update({
			'request': self.request,
			'to': to_email,
			'link': link
		})
		return PasswordResetEmail(user, context).send()


@csrf_protect
def password_reset(
	request,
	template_name='registration/password_reset_form.html',
	email_template_name='registration/password_reset_email.html',
	subject_template_name='registration/password_reset_subject.txt',
	password_reset_form=PasswordResetForm,
	token_generator=default_token_generator,
	post_reset_redirect='http://127.0.0.1:8000/login',
	from_email=None,
	current_app=None,
	extra_context=None,
	html_email_template_name=None
):
	"""
	a version of the password reset view from django.contrib.auth.views which accepts the
	email parameter in the querystring
	of a get request as well as the normal post. Not currently used.
	"""
	context = {}

	if post_reset_redirect is None:
		post_reset_redirect = reverse('password_reset_done')
	else:
		post_reset_redirect = resolve_url(post_reset_redirect)

	if request.method == "POST" or request.method == "GET":
		data = request.POST if request.method == "POST" else request.GET

		form = password_reset_form(data)
		if form.is_valid():
			opts = {
				'use_https': settings.SSL_ENABLED,
				'token_generator': token_generator,
				'from_email': from_email,
				'email_template_name': email_template_name,
				'subject_template_name': subject_template_name,
				'request': request,
				'html_email_template_name': html_email_template_name,
				'domain_override': request.get_host(),
			}
			form.save(**opts)
			return HttpResponseRedirect(post_reset_redirect)
	else:
		form = password_reset_form()
		context = {
			'form': form,
			'title': _('Password reset'),
		}
		if extra_context is not None:
			context.update(extra_context)

		if current_app is not None:
			request.current_app = current_app

	return TemplateResponse(request, template_name, context)

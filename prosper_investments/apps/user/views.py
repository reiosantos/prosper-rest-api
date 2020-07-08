import logging

from django.db import transaction
from django.db.models import Q
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, GenericAPIView, \
	CreateAPIView, ListAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet

from prosper_investments.apps.email.utils import WelcomeEmail, site_url, VerifyUserEmail
from prosper_investments.apps.permission.permissions import ManagementPermissions
from prosper_investments.apps.permission.serializers import VenuePermissionSerializer
from prosper_investments.apps.user import serializers
from prosper_investments.apps.user.models import DashboardSection, VenueViewerType
from prosper_investments.apps.user.pagination import UserInOrganisationPagination
from prosper_investments.apps.user.utils import (
	users_venue_permissions, user_exists_as_email, user_exists_as_mobile, filter_order_by,
	venues_permissions)
from prosper_investments.apps.venue.models import User, Venue

log = logging.getLogger('prosper_investments')


class RetrieveUserView(RetrieveModelMixin, GenericViewSet):
	"""
	Info about the current User.
	"""
	queryset = User.objects.all()
	permission_classes = (IsAuthenticated,)
	serializer_class = serializers.UserSerializer


class CurrentUserView(RetrieveAPIView):
	"""
	Info about the current User.
	"""
	serializer_class = serializers.UserSerializer

	def get_object(self):
		return self.request.user

	def get(self, request, *args, **kwargs):
		resp = self.retrieve(request)
		if resp and resp.data:
			log.debug(resp.data)
			# Update venues list that user has permission to working
			resp.data['venues'] = venues_permissions(resp.data)
		return resp


class EditProfileView(UpdateAPIView, GenericAPIView):
	"""
	Edit the currently logged in user's profile.
	{
		"firstName": "Reio",
		"lastName": "Santos",
		"mobile": 234567
	}
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
		return {'is_active': False, **super(CreateUserView, self).get_serializer_context()}

	@transaction.atomic
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
	{
		"user_id": "1" # gotten from the verifyEmail param from frontend link sent to first email
	}
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
		return None


class UserVenuePermissionsView(APIView):
	"""
	Get list of permissions for user and venue.
	params:
	- venue (from url parameter)
	- user (from authentication header)
	"""
	permission_classes = (IsAuthenticated,)

	serializer_class = VenuePermissionSerializer

	def get(self, request):
		if not request.venue:
			raise Venue.DoesNotExist('Venue was not passed to the request.')

		user_permissions = users_venue_permissions(request.venue, request.user)

		return Response(user_permissions)


class UserExistView(APIView):
	permission_classes = (AllowAny,)

	def get(self, request):
		if self.request.GET.get('mobile', False):
			return Response(user_exists_as_mobile(self.request.GET.get('mobile')))
		elif self.request.GET.get('email', False):
			return Response(user_exists_as_email(self.request.GET.get('email')))

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


class UsersInOrganisationViewSet(ModelViewSet):
	permission_classes = (ManagementPermissions,)
	serializer_class = serializers.UserInOrganisationSerializer
	pagination_class = UserInOrganisationPagination

	def get_queryset(self):
		"""
		search users in the organization
		query param: search, black, roles
		:return:
		"""
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

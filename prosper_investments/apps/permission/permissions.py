from rest_framework import permissions
from rest_framework.exceptions import ValidationError, NotAuthenticated

from prosper_investments.apps.user.models import User
from prosper_investments.apps.user.utils import user_has_venue_permission


def validate_perm(request):
	if not request.venue:
		raise ValidationError({'error': 'Venue Not Found'})

	user = request.user
	if not isinstance(user, User):
		raise NotAuthenticated({'error': 'Authentication credentials were not provided.'})

	return user


class AccountsView(permissions.BasePermission):
	def has_permission(self, request, view):
		user = validate_perm(request)
		return user.is_staff() and user_has_venue_permission(request.venue, user, 'account:view')


class AccountsCreate(permissions.BasePermission):
	def has_permission(self, request, view):
		user = validate_perm(request)
		return user.is_staff() and user_has_venue_permission(request.venue, user, 'account:create')


class IsVenueManager(permissions.BasePermission):
	def has_permission(self, request, view):
		user = validate_perm(request)
		return user.is_venue_manager(request.venue)


class IsVenueManagerOrReadOnly(IsVenueManager):
	def has_permission(self, request, view):
		user = validate_perm(request)
		if request.method == 'GET':
			return True
		elif request.method in ['POST', 'PUT', 'DELETE'] and user.is_venue_manager(request.venue):
			return True

		return None


class AllowGetOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		# allow all GET requests
		if request.method == 'GET':
			return True

		# Otherwise, only allow authenticated requests
		return request.user and request.user.is_authenticated


class ManagementPermissions(permissions.BasePermission):
	def has_permission(self, request, view):
		user = validate_perm(request)
		return user_has_venue_permission(request.venue, user, 'management')


class ForGetOrOtherPermissions(permissions.BasePermission):
	"""
	Permission for get to check if user is authenticated,
	for rest to have management permission.
	"""
	def has_permission(self, request, view):
		if not request.venue or not request.user.is_authenticated:
			raise ValidationError({'error': 'Venue Not Found or user not logged in'})

		user = request.user
		if request.method == 'GET':
			return user and user.is_authenticated

		return user_has_venue_permission(request.venue, user, 'management')

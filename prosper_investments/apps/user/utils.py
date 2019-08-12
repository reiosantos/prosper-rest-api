import uuid
from calendar import timegm
from datetime import datetime

from django.contrib.auth import get_user_model
from django.template import Template, Context
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_response_payload_handler

from prosper_investments.apps.common.psp_camel_case.util import camel_to_underscore
from prosper_investments.apps.user.models import DashboardSection, VenueViewerType, User
from prosper_investments.apps.venue.models import UsersVenues, UserData


def getattr_model_nested(instance, field):
	"""
	Get nested model field by dotted string, exmaple: 'user.first_name'
	"""

	def get_repr(value):
		if callable(value):
			return '%s' % value()
		return value

	def get_f(_instance, _field):
		field_path = _field.split('.')
		attr = _instance
		for elem in field_path:
			try:
				attr = get_repr(getattr(attr, elem))
			except AttributeError:
				return None
		return attr

	return get_repr(get_f(instance, field))


def get_username_field():
	# noinspection PyBroadException
	try:
		username_field = get_user_model().USERNAME_FIELD
	except:
		username_field = 'username'

	return username_field


def get_username(user):
	try:
		username = user.get_username()
	except AttributeError:
		username = user.username

	return username


def psp_jwt_payload_handler(user):
	username_field = get_username_field()
	username = get_username(user)

	payload = {
		'user_id': user.pk,
		'username': username,
		'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
	}
	if hasattr(user, 'email'):
		payload['email'] = user.email
	if isinstance(user.pk, uuid.UUID):
		payload['user_id'] = str(user.pk)

	payload[username_field] = username

	# Include original issued at time for a brand new token,
	# to allow token refresh
	if api_settings.JWT_ALLOW_REFRESH:
		payload['orig_iat'] = timegm(datetime.utcnow().utctimetuple())

	if api_settings.JWT_AUDIENCE is not None:
		payload['aud'] = api_settings.JWT_AUDIENCE

	if api_settings.JWT_ISSUER is not None:
		payload['iss'] = api_settings.JWT_ISSUER

	return payload


def psp_jwt_response_payload_handler(token, user=None, request=None):
	"""
	Adds 'is_venue_admin' boolean, which specifies whether or not the user is
	a venue-manager for the venue specified in the request.  If no request is
	specified, the key is not added.  Also ensures that the user is associated
	with the venue (for reporting purposes).
	"""

	data = jwt_response_payload_handler(token, user, request)

	if request and user and request.venue:
		data['is_venue_admin'] = user.is_venue_manager(request.venue)

		data['sections'] = DashboardSection.objects \
			.visible_to(user, request.venue).values_list('route_name', flat=True)

		ensure_user_associated_with_venue(user, request.venue)

	return data


def ensure_user_associated_with_venue(user, venue):
	"""
	Checks whether the user is associated with the venue, and if not,
	associates the user with the venue.
	"""
	UsersVenues.objects.get_or_create(user=user, venue=venue)


def user_has_venue_permission(venue, user, permission_name):
	"""
	Whether or not the user has the named permission at the venue in virtue of
	having a VenueViewerType at that Venue.

	This means the user has a global permission for all bookings at the venue.

	Returns:
		(bool)
	"""
	return VenueViewerType.objects.filter(
		venue=venue, users=user, permissions__permission_name=permission_name).exists()


def users_venue_permissions(venue, user):
	"""
	The names of any permissions the user has at a venue, in virtue of their
	venue-viewer-type(s).  These are permissions the user will have for all
	bookings at the venue.
	Returns:
		(ValuesListQuerySet)
	"""
	return VenueViewerType.objects.filter(venue=venue, users=user) \
		.values_list('permissions__permission_name', flat=True).distinct()


def user_exists_as_email(email):
	"""
	return true if email exists in this server
	"""
	return User.objects.filter(email=email).exists()


def user_exists_as_mobile(mobile):
	"""
	return if user exist in this server
	"""
	return UserData.objects.filter(mobile=mobile).exists()


def venues_permissions(company_user):
	"""
	return venues list that user has permission to working
	"""
	new_venue_list = []

	if company_user and company_user['venues_permissions']:
		venues_permissions_ = company_user['venues_permissions']
		venue_list = company_user['venues']

		for venue in venue_list:
			venue_name = venue['url_component']
			if venue_name in venues_permissions_:
				new_venue_list.append(venue)

	return new_venue_list


def filter_order_by(request, sqs):
	# Ordering
	order_by = request.GET.get('order')
	if order_by:
		# Strip off initial '+'
		if order_by.startswith('+'):
			order_by = order_by[1:]
		# Field name can arrive in camelCase
		order_by = camel_to_underscore(order_by)
		sqs = sqs.order_by(order_by)
	return sqs


class CustomTemplate(object):
	"""
	CustomTemplate class for templating <EXAMPLE> keys with instance values
	Examples for tamplete string:
		Scheduled/Checked In: <SCHEDULED_TIME_IN>/<ARRIVED_AT>
		Date: <DATE>

	Declare template map fields `template_booking_fields`
	TAG FIELD: instance field
	Example:
		{
		'BOOKING_REF': 'ref',
		'ACCESS_POINT': 'booking_vehicle.access_point_name'
		}
	Declare time fields `time_fields`, keys from `template_booking_fields` mapper
	It will be converted to venue format time
	Declare date fields `date_fields`, keys from `template_booking_fields` mapper
	It will be converted to venue format date
	"""

	template_booking_fields = {}
	time_fields = []
	date_fields = []

	def __init__(self, instance):
		self.instance = instance

	def render(self, string):
		"""
		Render template with real data values
		"""
		if not string:
			return string

		string = self.replace_chars(string)
		context = {}
		for key in self.template_booking_fields:
			context[key] = self.get_key_value(key)

		return Template(string).render(Context(context))

	def get_key_value(self, key):
		"""
		Get value for key with formating
		"""
		value = getattr_model_nested(self.instance, self.template_booking_fields[key])
		if value:
			if key in self.time_fields:
				# noinspection PyUnresolvedReferences
				value = value.strftime(self.instance.venue.formatted_time)
			elif key in self.date_fields:
				# noinspection PyUnresolvedReferences
				value = value.strftime(self.instance.venue.formatted_date)

			return value

	def replace_chars(self, string):
		string = string.replace('<%', '{{')
		string = string.replace('%>', '}}')
		return string


class UserCustomTemplate(CustomTemplate):
	"""
	UserCustomTemplate with booking map fields
	"""
	template_booking_fields = {
		'EMAIL': 'email',
		'FIRST_NAME': 'profile.first_name',
		'LAST_NAME': 'profile.last_name',
		'FULL_NAME': 'full_name',
		'MOBILE': 'profile.mobile',
		'ADDRESS1': 'profile.address1',
		'ADDRESS2': 'profile.address2',
		'CITY': 'profile.city',
		'COUNTRY': 'profile.country',
	}
	time_fields = []
	date_fields = []

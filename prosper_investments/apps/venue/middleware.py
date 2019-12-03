from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from prosper_investments.apps.venue.models import Venue


class VenueMiddleware(MiddlewareMixin):
	"""
	Add the Venue object to the request, if a venue query parameter is
	specified.
	"""
	def process_request(self, request):
		venue_url_component = request.GET.get('venue')
		request.venue = Venue.objects.filter(url_component=venue_url_component).first() \
			if venue_url_component else None


class RestrictStaffToAdminMiddleware(MiddlewareMixin):
	"""
	A middleware that restricts staff members access to administration panels.
	"""

	def process_request(self, request):
		if request.path.startswith(reverse('admin:index')):
			if request.user.is_authenticated:
				login = reverse('admin:login')
				logout = reverse('admin:logout')
				password_change = reverse('admin:password_change')
				password_change_done = reverse('admin:password_change_done')

				exclude_list = [login, logout, password_change, password_change_done]

				if request.path not in exclude_list and not request.user.is_staff():
					raise PermissionDenied({
						'error': 'You do not have permission to perform this action.'
					})

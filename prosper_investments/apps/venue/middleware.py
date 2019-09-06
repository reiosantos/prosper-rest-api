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

		return None

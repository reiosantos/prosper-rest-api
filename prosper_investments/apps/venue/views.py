import datetime
import logging

from django_countries.fields import Country
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from prosper_investments.apps.venue.models import Venue, VenueSetting, VenueSettingValue
from prosper_investments.apps.venue.serializers import VenueSettingValueSerializer, \
	ListVenueSerializer

log = logging.getLogger(__name__)


class VenueSettingsView(UpdateModelMixin, ListCreateAPIView):
	serializer_class = VenueSettingValueSerializer

	permission_classes = (AllowAny,)

	def get_queryset(self):
		venue = self.request.venue
		if not venue:
			raise ValidationError({'error': 'Invalid Venue'})
		return venue.setting_values.exclude(setting__var_define__isnull=True) \
			.select_related('setting')

	def list(self, request, *args, **kwargs):
		"""Add logo url"""

		queryset = self.get_queryset()
		serializer = self.get_serializer(queryset, many=True)
		data = serializer.data
		data += [{
			'path': 'venueName',
			'value': self.request.venue.name
		}, {
			'path': 'venueId',
			'value': self.request.venue.pk
		}, {
			'path': 'venueLocalTimeZone',
			'value': self.request.venue.local_timezone.zone
		}, {
			'path': 'venueLocalTimeZoneOffset',
			'value': datetime.datetime.now(self.request.venue.local_timezone).strftime('%z')
		}]
		return Response(data)


class VenuesListView(ListAPIView):
	"""
	List all venues.
	"""
	permission_classes = (AllowAny,)
	serializer_class = ListVenueSerializer
	queryset = Venue.objects.filter(active=True)


class VenueSettingsUpdateView(RetrieveUpdateAPIView):
	serializer_class = VenueSettingValueSerializer
	lookup_field = 'path'

	def get_object(self):
		try:
			setting = VenueSetting.objects.get(var_define=self.kwargs[self.lookup_field])
			obj = VenueSettingValue.objects.get_or_create(
				setting=setting, venue=self.request.venue)[0]
			self.check_object_permissions(self.request, obj)
			return obj
		except (TypeError, ValueError) as e:
			raise ValidationError({'error': e.message})

	def get_queryset(self):
		venue = self.request.venue
		if not venue:
			raise ValidationError({'error': 'Invalid venue'})
		return venue.setting_values.exclude(setting__var_define__isnull=True)


class CountriesView(APIView):
	"""
	Lists the countries at which there are venues.
	"""

	def get(self, request):
		country_codes = Venue.objects.filter(active=True).values_list('country', flat=True) \
			.distinct()

		data = list(map(lambda c: {'code': c, 'name': Country(code=c).name}, country_codes))
		return Response(data)


class ListVenuesView(ListAPIView):
	"""
	List the venues.
	"""
	serializer_class = ListVenueSerializer

	def get_queryset(self):
		country_code = self.kwargs.get('country')
		return Venue.objects.filter(active=True, country=country_code)

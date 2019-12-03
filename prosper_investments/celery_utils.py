from typing import Dict

from django.http import HttpRequest

from prosper_investments.apps.venue.models import Venue, User


def get_request(request_data):
	request = HttpRequest()
	request.META = request_data.get('meta', {})
	request.data = request_data.get('data', {})
	request.user = User.objects.get(pk=request_data.get('user_id', None))
	try:
		request.venue = Venue.objects.get(pk=request_data.get('venue_id', None))
	except Venue.DoesNotExist:
		request.venue = None
	return request


def remove_unserializable_attributes(data: Dict):
	for key in list(data):
		value = data[key]
		if type(value) == dict:
			remove_unserializable_attributes(value)
		elif type(value) not in [str, int, list]:
			data.pop(key)
	return data

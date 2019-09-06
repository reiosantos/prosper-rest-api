import logging

import requests
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from prosper_investments.apps.oauth.models import OAuthProvider, VenueToken
from prosper_investments.apps.venue.models import Venue

logger = logging.getLogger(__name__)


def get_venue_token(provider=None, venue=None, provider_name='', venue_name=''):
	try:
		provider = OAuthProvider.objects.get(name=provider_name) if (provider is None) else provider
		venue = Venue.objects.get(url_component=venue_name) if (venue is None) else venue
		return VenueToken.objects.get(provider=provider, venue=venue)
	except Venue.DoesNotExist:
		err_msg = 'Venue ' + venue_name + ' not found.'
		logger.error(err_msg)
		raise NotFound(err_msg)
	except OAuthProvider.DoesNotExist:
		err_msg = 'Unknown provider'
		logger.error(err_msg)
		raise NotFound(err_msg)
	except VenueToken.DoesNotExist:
		err_msg = 'Venue ' + venue_name + ' is not authenticated for provider ' + provider_name
		logger.error(err_msg)
		raise NotFound(err_msg)


def _refresh(provider, venue):
	try:
		venue_token = VenueToken.objects.get(provider=provider, venue=venue)
		resp = requests.post(provider.token_url, verify=False, params={
			"grant_type": 'refresh_token',
			"refresh_token": venue_token.refresh_token,
			"client_id": provider.client_id,
			"client_secret": provider.client_secret
		})
		if resp.status_code == requests.codes.ok:
			resp_json = resp.json()
			venue_token.oauth_token = resp_json['access_token']
			venue_token.refresh_token = resp_json['refresh_token']
			venue_token.save()
			return Response(venue_token, status=status.HTTP_200_OK)
		return Response({"error_description": get_error(resp)}, status=resp.status_code)
	except VenueToken.DoesNotExist:
		raise NotFound(
			'Venue ' + venue.name + ' is not authenticated for provider ' + provider.name)
	except Exception as e:
		return handle_error(e)


def get_error(resp):
	resp_json = resp.json()
	err_message = ''
	if 'error_description' in resp_json:
		err_message = resp_json['error_description']
	elif 'errors' in resp_json:
		err_message = resp_json['errors']
	elif 'error' in resp_json:
		err_message = resp_json['error']
	return err_message


def handle_error(e: Exception):
	return Response({"error_description": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

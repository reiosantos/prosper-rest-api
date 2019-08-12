import logging
import os

import requests
from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from prosper_investments.apps.oauth import util
from prosper_investments.apps.oauth.models import OAuthProvider, VenueToken
from prosper_investments.apps.oauth.serializers import OAuthProviderSerializer, \
	VenueTokenSerializer, APIProviderSerializer

logger = logging.getLogger(__name__)


# Generic OAuth API calls


@api_view(['GET'])
def authorize(request):
	try:
		provider_name = request.GET.get('provider', '')
		provider = OAuthProvider.objects.get(name=provider_name)
		serializer = OAuthProviderSerializer(provider, venue=request.venue)
		return Response(serializer.data)
	except Exception as e:
		logger.error(e)
		return util.handle_error(e)


@api_view(['GET'])
def token(req):
	"""
		Expected params:
		* {{provider}} - Chosen provider
		* {{venue}} - Chosen venue for which an OAuth token should be retrieved
		* {{code}} - One-time code with which user has been redirected from ProCore authorization page
	"""
	try:
		provider_name = req.GET.get('provider', '')
		venue = req.venue
		code = req.GET.get('code', 'code')
		provider = OAuthProvider.objects.get(name=provider_name)
		redirect_url = provider.redirect_url
		if os.environ.get('ENV') != 'local':
			redirect_url = redirect_url % req.venue.url_component

		logger.info('OAuthProvider.redirect_url:  %s' % redirect_url)
		resp = requests.post(provider.token_url, verify=False, params={
			'grant_type': 'authorization_code',
			'code': code,
			'client_id': provider.client_id,
			'redirect_uri': redirect_url,
			'client_secret': provider.client_secret
		})
		if resp.status_code == requests.codes.ok:
			resp_json = resp.json()
			venue_token = VenueToken(
				oauth_token=resp_json['access_token'],
				refresh_token=resp_json['refresh_token'],
				venue=venue,
				provider=provider
			)
			if provider_name.startswith('stripe'):
				venue_token.stripe_user_id = resp_json['stripe_user_id']
				venue_token.stripe_publishable_key = resp_json['stripe_publishable_key']
			venue_token.save()
			return Response(resp_json)
		return Response({"error_description": util.get_error(resp)}, status=resp.status_code)
	except Exception as e:
		return util.handle_error(e)


@api_view(['GET'])
def is_authenticated(req):
	provider_name = req.GET.get('provider', '')
	status = VenueToken.has_active_provider(provider_name, req.venue.name)

	use_stripe_main_account = req.venue.get_setting_value('USE_STRIPE_MAIN_ACCOUNT')
	if use_stripe_main_account and bool(int(use_stripe_main_account)):
		status = True

	return Response({"status": status})


class VenueTokenViewSet(viewsets.ModelViewSet):
	permission_classes = (AllowAny,)
	queryset = VenueToken.objects.all()
	serializer_class = VenueTokenSerializer
	lookup_field = 'provider'

	def get_object(self):
		try:
			use_stripe_main_account = self.request.venue.get_setting_value(
				'USE_STRIPE_MAIN_ACCOUNT')

			if use_stripe_main_account and bool(int(use_stripe_main_account)):
				try:
					obj = OAuthProvider.objects.get(name=self.kwargs[self.lookup_field])
					obj = {
						'stripe_user_id': None,
						'refresh_token': None,
						'stripe_publishable_key': obj.publishable_key,
						'oauth_token': obj.client_secret,
						'provider': obj,
						'venue': self.request.venue
					}
				except OAuthProvider.DoesNotExist:
					obj = VenueToken.objects.get(
						provider__name=self.kwargs[self.lookup_field], venue=self.request.venue)
					self.check_object_permissions(self.request, obj)
			else:
				obj = VenueToken.objects.get(
					provider__name=self.kwargs[self.lookup_field], venue=self.request.venue)
				self.check_object_permissions(self.request, obj)

			return obj
		except (TypeError, ValueError, VenueToken.DoesNotExist):
			raise Http404


class ProviderViewSet(viewsets.ReadOnlyModelViewSet):
	permission_classes = (AllowAny,)
	serializer_class = APIProviderSerializer
	queryset = OAuthProvider.objects.all()
	lookup_field = 'name'

	'''
	OAuthProvider.redirect_url can have %s in it's name because of our urlcomponent url scheme.
	Here we just apply the venue value.
	'''

	def get_object(self):
		try:
			obj = OAuthProvider.objects.get(name=self.kwargs[self.lookup_field])
			self.check_object_permissions(self.request, obj)
			if os.environ.get('ENV') != 'local':
				obj.redirect_url = obj.redirect_url % self.request.venue.url_component
			return obj
		except (TypeError, ValueError, VenueToken.DoesNotExist):
			raise Http404

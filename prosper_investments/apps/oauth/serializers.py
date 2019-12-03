from rest_framework import serializers

from prosper_investments.apps.oauth.models import VenueToken, OAuthProvider


class VenueTokenSerializer(serializers.ModelSerializer):
	oauth_token = serializers.CharField(max_length=250)
	refresh_token = serializers.CharField(max_length=250)

	class Meta:
		model = VenueToken
		fields = (
			'provider', 'venue', 'oauth_token', 'refresh_token', 'stripe_user_id',
			'stripe_publishable_key')

	def create(self, validated_data):
		return VenueToken.objects.create(**validated_data)

	def update(self, instance, validated_data):
		instance.access_token = validated_data.get('access_token', instance.access_token)
		instance.refresh_token = validated_data.get('refresh_token', instance.refresh_token)
		instance.save()
		return instance


class OAuthProviderSerializer(serializers.ModelSerializer):
	redirect_url = serializers.SerializerMethodField()
	venue = ""

	def __init__(self, *args, **kwargs):
		self.venue = kwargs.pop('venue', None)
		super(OAuthProviderSerializer, self).__init__(*args, **kwargs)

	def get_redirect_url(self, obj):
		try:
			return obj.redirect_url % self.venue.url_component
		except TypeError:
			return obj.redirect_url

	class Meta:
		model = OAuthProvider
		fields = (
			'name', 'client_id', 'client_secret', 'authorize_url',
			'api_url', 'token_url', 'redirect_url', 'publishable_key')


class APIProviderSerializer(serializers.ModelSerializer):

	def __init__(self, *args, **kwargs):
		super(APIProviderSerializer, self).__init__(*args, **kwargs)

	class Meta:
		model = OAuthProvider
		fields = (
			'name', 'client_id', 'client_secret', 'authorize_url',
			'api_url', 'token_url', 'redirect_url', 'publishable_key')

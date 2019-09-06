from django.db import models

from prosper_investments.apps.venue.models import Venue


class OAuthProvider(models.Model):
	name = models.CharField(max_length=100, null=False)
	client_id = models.CharField(max_length=100, null=False)
	client_secret = models.CharField(max_length=100, null=False)

	publishable_key = models.CharField(max_length=250, null=True)
	authorize_url = models.CharField(max_length=100, null=False)
	api_url = models.CharField(max_length=100, null=False)
	token_url = models.CharField(max_length=100, null=False)
	redirect_url = models.CharField(max_length=100, null=False)

	def __str__(self):
		return self.name

	class Meta:
		db_table = 'psp_oauth_providers'


class VenueToken(models.Model):
	provider = models.ForeignKey(
		OAuthProvider, db_column='oauth_provider_id', related_name='venue_tokens',
		on_delete=models.CASCADE
	)
	venue = models.ForeignKey(Venue, db_column='psp_venue_id', on_delete=models.CASCADE)

	oauth_token = models.TextField(blank=False, null=False)
	refresh_token = models.TextField(blank=False, null=False)
	created_at = models.BigIntegerField(null=True)
	expires_in = models.BigIntegerField(null=True)
	token_type = models.CharField(max_length=100, null=True)
	stripe_user_id = models.CharField(max_length=100, null=True)
	stripe_publishable_key = models.CharField(max_length=100, null=True)

	unique_together = ('provider', 'venue')

	@staticmethod
	def has_active_provider(provider_name, venue_name):
		try:
			venue_token = VenueToken.objects.get(
				models.Q(provider__name=provider_name) &
				models.Q(venue__name=venue_name)
			)
			if venue_token is not None:
				return True
			return False
		except VenueToken.DoesNotExist:
			return False

	class Meta:
		db_table = 'psp_oauth_venue_tokens'

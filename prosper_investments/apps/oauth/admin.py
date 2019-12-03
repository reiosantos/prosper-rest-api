from django.contrib import admin

from prosper_investments.apps.oauth.models import (OAuthProvider, VenueToken)

admin.site.register(OAuthProvider)
admin.site.register(VenueToken)

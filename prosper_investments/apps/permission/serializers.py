from rest_framework import serializers

from prosper_investments.apps.permission.models import VenuePermission


class VenuePermissionSerializer(serializers.ModelSerializer):
	class Meta:
		model = VenuePermission
		fields = ('permission_name',)

from rest_framework import serializers

from prosper_investments.apps.permission.models import ContributionPermission


class ContributionPermissionSerializer(serializers.ModelSerializer):
	class Meta:
		model = ContributionPermission
		fields = ('permission_name',)

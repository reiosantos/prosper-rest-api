from rest_framework.viewsets import ModelViewSet

from prosper_investments.apps.permission.models import ContributionPermission
from prosper_investments.apps.permission.permissions import ManagementPermissions
from prosper_investments.apps.permission.serializers import ContributionPermissionSerializer


class ContributionPermissionViewSet(ModelViewSet):
	serializer_class = ContributionPermissionSerializer
	permission_classes = (ManagementPermissions,)

	def get_queryset(self):
		return ContributionPermission.objects.filter(venue=self.request.venue)

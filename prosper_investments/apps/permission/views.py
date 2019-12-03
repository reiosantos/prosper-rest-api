from rest_framework.generics import ListAPIView

from prosper_investments.apps.permission.models import ContributionPermission
from prosper_investments.apps.permission.permissions import ManagementPermissions
from prosper_investments.apps.permission.serializers import ContributionPermissionSerializer


class ContributionPermissionListView(ListAPIView):
	serializer_class = ContributionPermissionSerializer
	permission_classes = (ManagementPermissions,)
	queryset = ContributionPermission.objects.all()

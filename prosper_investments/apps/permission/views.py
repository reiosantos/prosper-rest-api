from rest_framework.generics import ListAPIView

from prosper_investments.apps.permission.models import VenuePermission
from prosper_investments.apps.permission.permissions import ManagementPermissions
from prosper_investments.apps.permission.serializers import VenuePermissionSerializer


class VenuePermissionListView(ListAPIView):
	serializer_class = VenuePermissionSerializer
	permission_classes = (ManagementPermissions,)
	queryset = VenuePermission.objects.all()

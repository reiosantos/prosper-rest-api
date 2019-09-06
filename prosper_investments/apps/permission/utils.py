from prosper_investments.apps.permission.models import ContributionPermission
from prosper_investments.apps.user.constants import VIEWER_TYPE_MANAGER
from prosper_investments.apps.user.models import VenueViewerType


def make_user_venue_manager(user, venue):
	venue_manager, created = VenueViewerType.objects.get_or_create(
		venue=venue, name=VIEWER_TYPE_MANAGER)

	if created:
		venue_manager.permissions = ContributionPermission.objects.all()

	venue_manager.users.add(user)

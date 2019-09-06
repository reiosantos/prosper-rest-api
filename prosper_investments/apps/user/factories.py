import factory

from prosper_investments.apps.permission.models import ContributionPermission
from prosper_investments.apps.user.models import DashboardSection, VenueViewerType


class VenueViewerTypeFactory(factory.DjangoModelFactory):
	class Meta:
		model = VenueViewerType

	@factory.post_generation
	def route_names(self, create, extracted, **kwargs):

		if not create:
			return

		if extracted:
			for route_name in extracted:
				section, _ = DashboardSection.objects.get_or_create(
					route_name=route_name, name=route_name)
				self.sections.add(section)

	@factory.post_generation
	def permission_names(self, create, extracted, **kwargs):

		if not create:
			return

		if extracted:
			for permission_name in extracted:
				permission = ContributionPermission.objects.get(
					permission_name=permission_name
				)
				self.permissions.add(permission)

	@factory.post_generation
	def permissions(self, create, extracted, **kwargs):

		if not create:
			return

		if extracted:
			self.permissions = extracted

	@factory.post_generation
	def users(self, create, extracted, **kwargs):

		if not create:
			return

		if extracted:
			for user in extracted:
				self.users.add(user)

from random import randint

import factory
from factory import Factory as FakerFactory

from prosper_investments.apps.venue.models import Venue, User, Role, UserData, UsersAdminVenues


class VenueFactory(factory.DjangoModelFactory):
	class Meta:
		model = Venue

	name = factory.Sequence(lambda n: 'Venue %d' % n)
	url_component = factory.LazyAttribute(
		lambda a: '{0}-{1}'.format(FakerFactory.create().slug(), randint(1, 1000)))

	active = 1


class UserDataFactory(factory.DjangoModelFactory):
	first_name = factory.Faker('first_name')
	last_name = factory.Faker('last_name')
	address1 = factory.Faker('secondary_address')
	address2 = factory.Faker('street_address')
	city = factory.Faker('city')
	country = factory.Faker('country')

	class Meta:
		model = UserData


class RoleFactory(factory.DjangoModelFactory):
	class Meta:
		model = Role

	name = factory.Sequence(lambda n: 'Role %d' % n)


class UserFactory(factory.DjangoModelFactory):
	"""An active, non-admin user with a fresh Company and Role"""

	class Meta:
		model = User

	email = factory.Faker('email')
	password = factory.PostGenerationMethodCall('set_password', 'default-password')
	is_active = True
	is_admin = False
	role = factory.SubFactory(RoleFactory)
	profile = factory.RelatedFactory(UserDataFactory, 'user')


class UsersAdminVenuesFactory(factory.DjangoModelFactory):
	class Meta:
		model = UsersAdminVenues

	venue = factory.SubFactory(VenueFactory)

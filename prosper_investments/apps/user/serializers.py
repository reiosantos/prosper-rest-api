import logging

from django.db import transaction
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from prosper_investments.apps.permission.models import ContributionPermission
from prosper_investments.apps.user.models import User, DashboardSection, VenueViewerType
from prosper_investments.apps.user.utils import ensure_user_associated_with_venue
from prosper_investments.apps.venue.documents import UserDocument
from prosper_investments.apps.venue.models import Venue, Role, UserData
from prosper_investments.apps.venue.relations import ForThisVenuePrimaryKeyRelatedField

log = logging.getLogger('prosper_investments')


class UserVenueSerializer(serializers.ModelSerializer):
	url = serializers.CharField(source='rest_api_url')

	class Meta:
		model = Venue
		fields = ('name', 'url_component', 'url')


class UserProfileSerializer(serializers.ModelSerializer):
	mobile = serializers.CharField(allow_blank=True, required=False)
	address1 = serializers.CharField(allow_blank=True, required=False)
	address2 = serializers.CharField(allow_blank=True, required=False)
	city = serializers.CharField(allow_blank=True, required=False)
	country = serializers.CharField(allow_blank=True, required=False)

	class Meta:
		model = UserData
		fields = ('first_name', 'last_name', 'mobile', 'address1', 'address2', 'city', 'country',)

	def update(self, instance, validated_data):
		try:
			if (
				instance.mobile != validated_data['mobile'] and
				validated_data.get('mobile_confirmed', False) is not True
			):
				validated_data['mobile_confirmed'] = False

			return super(UserProfileSerializer, self).update(instance, validated_data)
		except KeyError as e:
			raise KeyError(f"Field {str(e)} is required")


class UserSerializer(serializers.ModelSerializer):
	mobile = serializers.CharField(source='profile.mobile', allow_blank=True, required=False)
	first_name = serializers.CharField(source='profile.first_name')
	last_name = serializers.CharField(source='profile.last_name')
	address1 = serializers.CharField(source='profile.address1', allow_blank=True, required=False)
	address2 = serializers.CharField(source='profile.address2', allow_blank=True, required=False)
	city = serializers.CharField(source='profile.city', allow_blank=True, required=False)
	country = serializers.CharField(source='profile.country', allow_blank=True, required=False)
	mobile_confirmed = serializers.CharField(
		source='profile.mobile_confirmed', allow_blank=True, required=False)
	venues = UserVenueSerializer(many=True, read_only=True)
	user_type = serializers.StringRelatedField(source='user_type.name')
	user_role = serializers.StringRelatedField(source='role.name')

	sections = serializers.SerializerMethodField()
	permissions = serializers.SerializerMethodField()
	venues_permissions = serializers.SerializerMethodField()

	class Meta:
		model = User
		document = UserDocument
		fields = (
			'email',
			'mobile',
			'user_type',
			'user_role',
			'first_name',
			'last_name',
			'address1',
			'address2',
			'city',
			'country',
			'mobile_confirmed',
			'sections',
			'permissions',
			'venues',
			'venues_permissions'
		)

	def get_sections(self, instance):
		venue = self.context.get('request').venue
		return DashboardSection.objects.visible_to(instance, venue).values_list(
			'route_name', flat=True)

	def get_permissions(self, instance):
		venue = self.context.get('request').query_params.get('venue')
		return instance.viewer_types.filter(venue__url_component=venue) \
			.values_list('permissions__permission_name', flat=True)

	def get_venues_permissions(self, instance):
		venues_permissions = {}

		for venue in instance.venues.values():
			venue_name = venue['url_component']
			if venue_name:
				permission = instance.viewer_types.filter(venue__url_component=venue_name) \
					.values_list('permissions__permission_name', flat=True)
				if permission:
					venues_permissions[venue_name] = permission
		return venues_permissions


class EditUserSerializer(UserSerializer):
	def update(self, instance, validated_data):

		profile_data = None
		try:
			profile_data = validated_data.pop('profile')
		except KeyError:
			if not self.partial:
				raise ParseError({'error': "Missing profile information"})

		super(EditUserSerializer, self).update(instance, validated_data)

		if profile_data:
			try:
				profile = instance.profile
			except User.profile.RelatedObjectDoesNotExist:
				profile = UserData()

			instance.profile = profile
			instance.profile.user = instance
			UserProfileSerializer().update(instance.profile, profile_data)

		return instance


class CreateUserSerializer(UserSerializer):
	def create(self, validated_data):
		try:
			is_active = self.context.get("is_active", True)
			# Create the user profile
			profile_data = validated_data.pop('profile', {'mobile': ''})

			with transaction.atomic():
				profile_data['user'] = User.objects.create_user(
					role=Role.objects.get_or_create(name='Role')[0],
					email=validated_data['email'],
					password=validated_data['password'],
					is_active=is_active
				)
				UserData.objects.create(**profile_data)
				# only do this if user signup for venue, if not venue skip it
				venue = self.context.get("request").venue if self.context.get("request") else None
				if venue:
					ensure_user_associated_with_venue(profile_data['user'], venue)

			return profile_data['user']

		except KeyError:
			raise ParseError({'error': "Some data was missing"})

	class Meta(UserSerializer.Meta):
		model = UserSerializer.Meta.model
		document = UserSerializer.Meta.document
		fields = UserSerializer.Meta.fields + ('password',)
		write_only_fields = ('password',)


class ActivateUserSerializer(UserSerializer):
	def update(self, instance, validated_data):
		instance.is_active = True
		instance.save()
		return instance


class UserInOrganisationSerializer(serializers.ModelSerializer, DocumentSerializer):
	roles = ForThisVenuePrimaryKeyRelatedField(
		source='viewer_types',
		many=True,
		queryset=VenueViewerType.objects.all(),
	)

	first_name = serializers.CharField(source='profile.first_name', read_only=True)
	last_name = serializers.CharField(source='profile.last_name', read_only=True)

	def update(self, instance, validated_data):
		return super(UserInOrganisationSerializer, self).update(instance, validated_data)

	def get_full_name(self, instance):
		try:
			return '%s %s' % (instance.first_name, instance.last_name,)
		except UserData.DoesNotExist:
			return ''

	class Meta:
		model = User
		document = UserDocument
		fields = (
			'id',
			'roles',
			'email',
			'first_name',
			'last_name',
			'full_name',
			'date_joined'
		)
		read_only_fields = (
			'email',
			'first_name',
			'last_name',
			'full_name',
			'date_joined',
		)


class UserInOrganisationShortSerializer(serializers.ModelSerializer):
	first_name = serializers.CharField(source='profile.first_name', read_only=True)
	last_name = serializers.CharField(source='profile.last_name', read_only=True)

	def get_full_name(self, instance):
		try:
			return '%s %s' % (instance.first_name, instance.last_name,)
		except UserData.DoesNotExist:
			return ''

	class Meta:
		model = User
		fields = (
			'id',
			'email',
			'first_name',
			'last_name',
			'full_name',
		)
		read_only_fields = (
			'email',
			'first_name',
			'last_name',
			'full_name',
		)


class DashboardSectionSerializer(serializers.ModelSerializer):
	value = serializers.CharField(source='route_name')
	display_name = serializers.CharField(source='name')

	class Meta:
		model = DashboardSection
		fields = (
			'value',
			'display_name',
		)


class VenueViewerTypeSerializer(serializers.ModelSerializer):
	value = serializers.IntegerField(source='pk', read_only=True)
	display_name = serializers.CharField(source='name')

	sections = serializers.SlugRelatedField(
		slug_field='route_name',
		queryset=DashboardSection.objects.all(),
		many=True,
	)

	permissions = serializers.SlugRelatedField(
		slug_field='permission_name',
		queryset=ContributionPermission.objects.all(),
		many=True,
		required=False
	)

	class Meta:
		model = VenueViewerType
		fields = (
			'value',
			'display_name',
			'sections',
			'permissions'
		)

	def create(self, validated_data):
		validated_data['venue'] = self.context['request'].venue
		return super(VenueViewerTypeSerializer, self).create(validated_data)

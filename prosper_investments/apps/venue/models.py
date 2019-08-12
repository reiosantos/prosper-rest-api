from datetime import datetime
from typing import Union

import pytz
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django_countries.fields import CountryField
from timezone_field import TimeZoneField

from prosper_investments.apps.common.fields import LowerCaseCharField
from prosper_investments.apps.common.util import convert_to_python_date_string_format
from prosper_investments.apps.user.constants import VIEWER_TYPE_MANAGER


class Venue(models.Model):
	# Use this with the datetime.strftime method
	TIME_FORMAT = '%I:%M %p'
	WELCOME_TEMPLATE = 'psp-user-welcome-con'

	name = models.CharField(max_length=100, blank=True, null=True)
	address = models.TextField(blank=True, null=True)
	active = models.IntegerField()
	url_component = LowerCaseCharField(
		max_length=200, blank=True, null=True, db_column='url', unique=True)
	users = models.ManyToManyField('User', through='UsersVenues')
	local_timezone = TimeZoneField(default='Europe/London')
	country = CountryField(default='GB')
	language_code = models.CharField(max_length=7, choices=LANGUAGES, default='en-gb')

	def __str__(self):
		return self.name

	class Meta:
		db_table = 'psp_venues'

	def get_setting_value(self, setting_variable, default=None):
		try:
			return VenueSettingValue.objects.filter(
				setting__var_define=setting_variable, venue=self).get().value
		except VenueSettingValue.DoesNotExist:
			return default

	def set_setting_value(self, setting_variable, value: Union[str, int]):
		"""
		Set a setting on this venue.
		Args:
			setting_variable (string): The name of the setting
			value (Union[str, int])): The value of the variable
		"""
		setting_value, created = self.setting_values.get_or_create(
			setting=VenueSetting.objects.get_or_create(var_define=setting_variable)[0],
			defaults={'value': value}
		)
		if not created and setting_value != value:
			setting_value.value = value
			setting_value.save()

	@property
	def support_email_address(self):
		"""Email address for support requests for the Venue"""
		return '%s-%s' % (self.url_component, settings.DEFAULT_SUPPORT_EMAIL)

	@property
	def dashboard_url(self):
		return settings.PSP_DASHBOARD_URL % self.url_component \
			if "%s" in settings.PSP_DASHBOARD_URL else settings.PSP_DASHBOARD_URL

	@property
	def rest_api_url(self):
		return settings.PSP_REST_API_BASE_URL % self.url_component \
			if "%s" in settings.PSP_REST_API_BASE_URL else settings.PSP_REST_API_BASE_URL

	@property
	def formatted_time(self):
		venue_time = self.get_setting_value('dateFormat.shortTime', 'HH:mm')
		return convert_to_python_date_string_format(venue_time)

	@property
	def formatted_date(self):
		venue_time = self.get_setting_value('dateFormat.mediumDate', 'yyyy-MMM-dd')
		return convert_to_python_date_string_format(venue_time)

	@property
	def formatted_datetime(self):
		venue_time = self.get_setting_value('dateFormat.medium', 'yyyy-MMM-dd HH:mm')
		return convert_to_python_date_string_format(venue_time)

	def get_in_local_time(self, time_to_convert):
		"""
		Converts naive python datetime (without tzinfo) into venue's local time zone.
		Does not touch time, just sets timezone
		:param time_to_convert: datetime.datetime to be converted
		:return: non-naive datetime.datetime with tzinfo set to venue's timezone
		"""
		if not time_to_convert:
			return None
		timezone = pytz.timezone(str(self.local_timezone))
		return timezone.localize(time_to_convert)

	def get_in_local_time_shifted(self, time_to_convert):
		"""
		Convert naive datetime to timezone with calculated offset.
		"""
		dt = self.get_in_local_time(time_to_convert)
		offset = dt.utcoffset()
		return (dt + offset).replace(tzinfo=None)


class Role(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name

	class Meta:
		db_table = 'psp_roles'


class UserManager(BaseUserManager):
	use_in_migrations = True

	def _create_user(self, email, password, is_admin, is_active=True, role=None, **extra_fields):
		"""
		Creates and saves a User with the given username, email and password.
		"""

		if not role:
			if is_admin:
				role = Role.objects.get_or_create(name='SuperAdmin')[0]
			else:
				raise ValueError('You must specify a Role')

		if not email:
			raise ValueError('The given username/email must be set')

		email = self.normalize_email(email)
		user = self.model(
			email=email, role=role, is_active=is_active, is_admin=is_admin,
			date_joined=datetime.now(), **extra_fields)

		user.set_password(password)
		user.save()
		return user

	def create_user(self, email, password=None, **extra_fields):
		return self._create_user(email, password, False, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		return self._create_user(email, password, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	"""
	Voyage Control user profile
	"""
	email = models.EmailField(max_length=100, blank=True, null=True, unique=True, db_index=True)
	is_active = models.BooleanField(db_column='active')
	date_joined = models.DateTimeField(db_column='dt', blank=True, null=True, default=datetime.now)
	role = models.ForeignKey(Role, db_column='psp_roles_id', on_delete=models.SET_NULL, null=True)
	is_admin = models.NullBooleanField(db_column='isadmin')
	venues = models.ManyToManyField(Venue, through='UsersVenues')

	REQUIRED_FIELDS = []
	USERNAME_FIELD = 'email'

	objects = UserManager()

	def is_staff(self):
		return self.is_admin

	def is_superuser(self):
		return self.is_admin

	def is_venue_manager(self, venue):
		"""
		Whether or not the user is a 'manager' / 'admin' at a given venue.
		"""
		return self._manager_viewer_types().filter(venue=venue).exists()

	def _manager_viewer_types(self):
		return self.viewer_types.filter(name=VIEWER_TYPE_MANAGER)

	def get_short_name(self):
		return self.email

	def get_full_name(self):
		return self.full_name

	# Grappelli autocomplete
	@staticmethod
	def autocomplete_search_fields():
		return (
			'profile__first_name__icontains',
			'profile__last_name__icontains',
			'email__icontains',
		)

	def __str__(self):
		return self.email

	class Meta:
		db_table = 'psp_users'

	@property
	def full_name(self):
		try:
			return '%s %s' % (self.profile.first_name, self.profile.last_name,)
		except UserData.DoesNotExist:
			return ''


class UserData(models.Model):
	first_name = models.CharField(max_length=100, db_column='name', blank=True, null=True)
	last_name = models.CharField(max_length=100, db_column='lastname', blank=True, null=True)
	user = models.OneToOneField(
		User, db_column='psp_users_id', related_name='profile', on_delete=models.CASCADE)
	mobile = models.CharField(max_length=45, blank=True, null=True)
	address1 = models.CharField(max_length=200)
	address2 = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	mobile_confirmed = models.BooleanField(default=False)

	class Meta:
		db_table = 'psp_users_data'


class UsersVenues(models.Model):
	user = models.ForeignKey(User, db_column='psp_user_id', on_delete=models.CASCADE)
	venue = models.ForeignKey(Venue, db_column='psp_venue_id', on_delete=models.CASCADE)

	class Meta:
		verbose_name_plural = 'Users Venues'
		db_table = 'psp_users_venues'
		unique_together = (('user', 'venue',),)


class VenueSetting(models.Model):
	label = models.CharField(max_length=200, blank=True, null=True)
	CHOICES_KEY = (
		('dateFormat.shortTime', 'Time format (e.g. HH:mm)'),
		('dateFormat.mediumDate', 'Date format (e.g. dd-MMM-yyy)'),
		('dateFormat.medium', 'Date format with time (e.g. dd-MMM-yyyy HH:mm)'),
		('dateFormat.full', 'Date format with day-of-week and time (e.g. EEE d MMM HH:mm)'),
		('TERMS_URL', 'T&C link'),
		('PRIVACY_POLICY_URL', 'Privacy Policy link'),
		('DEFAULT_LANGUAGE_CODE', 'Default language (example: en-us)'),
		('ENABLE_DEPOSIT', 'Enable usage of the Deposit system for payments'),
		('DEFAULT_CURRENCY',
		 'Default currency for the Deposit system (example: usd, ush,...)'),
		('MANDATORY_CREDIT_CARD',
		 'User must enter their credit card info before being able to add a contribution'),
		('STARTING_DAY_IN_WEEK',
		 'Starting day in week for calendar, format: 0=Sunday, 1=Monday, 2=Tuesday, 3=Wednesday,'
		 ' 4=Thursday, 5=Friday, 6=Saturday'),
		('VENUE_ADMIN_EMAIL', 'Venue Admin email'),
		('HIDE_DATE_AND_TIME_HEADER_BAR', 'Hide date and time in the header bar'),
		('HIDE_DRIVER_CHECKBOX', 'Hide driver checkbox'),
		('USE_STRIPE_MAIN_ACCOUNT', 'Enable Use of stripe main account')
	)

	DICT_OF_CHOICES = {key: value for (key, value) in CHOICES_KEY}

	var_define = models.CharField(max_length=100, choices=CHOICES_KEY, unique=True, null=True)

	class Meta:
		db_table = 'psp_venue_settings'

	def __str__(self):
		return self.DICT_OF_CHOICES.get(self.var_define, self.var_define)


class VenueSettingValue(models.Model):
	setting = models.ForeignKey(VenueSetting, db_column='psp_setting_id', on_delete=models.CASCADE)
	venue = models.ForeignKey(
		Venue, db_column='psp_venue_id', related_name='setting_values', on_delete=models.CASCADE)
	value = models.TextField(blank=True, null=True, db_column='psp_value')

	class Meta:
		db_table = 'psp_venue_settings_values'
		# Setting must be unique for Venue.
		unique_together = (('venue', 'setting',),)

	def __str__(self):
		return '%s %s: %s' % (self.venue, self.setting, self.value)

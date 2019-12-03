import pytz
from django.db import models
from django.utils.functional import cached_property


class ContributionStatus(models.Model):
	STATUS_APPROVED = 0
	STATUS_REJECTED = 1
	STATUS_DECLINED = 2  # If approval is needed, a booking can be declined.
	STATUS_CANCELLED = 4

	STATUS_APPROVED_STR = 'Approved'
	STATUS_REJECTED_STR = 'Rejected'
	STATUS_DECLINED_STR = 'Declined'
	STATUS_CANCELLED_STR = 'Cancelled'

	STATUS_CHOICES = (
		(STATUS_APPROVED, STATUS_APPROVED_STR),
		(STATUS_REJECTED, STATUS_REJECTED_STR),
		(STATUS_DECLINED, STATUS_DECLINED_STR),
		(STATUS_CANCELLED, STATUS_CANCELLED_STR),
	)

	EDIT_STATUS = 'edit'
	EDIT_RELATED_STATUSES = [
		STATUS_APPROVED,
	]

	DICT_OF_STATUSES = {key: value for (key, value) in STATUS_CHOICES}

	PREFIX_CREATE = 'status:create:'
	PREFIX_DELETE = 'status:delete:'

	@classmethod
	def get_status_name(cls, status):
		if status == cls.STATUS_REJECTED:
			return cls.STATUS_REJECTED_STR
		elif status == cls.STATUS_DECLINED:
			return cls.STATUS_DECLINED_STR
		elif status == cls.STATUS_CANCELLED:
			return cls.STATUS_CANCELLED_STR
		elif status == cls.STATUS_APPROVED:
			return cls.STATUS_APPROVED_STR

	@classmethod
	def action_create(cls, status):
		return '%s%d' % (cls.PREFIX_CREATE, status)

	@classmethod
	def action_delete(cls, status):
		return '%s%d' % (cls.PREFIX_DELETE, status)

	status = models.IntegerField(choices=STATUS_CHOICES, db_column='status_id', db_index=True)
	created_by = models.ForeignKey('venue.User', null=True, default=None, on_delete=models.SET_NULL)
	when_recorded = models.DateTimeField(db_column='dt')

	class Meta:
		verbose_name_plural = 'Contribution Statuses'
		db_table = 'psp_status'

	@cached_property
	def utc_datetime(self):
		"""
		When the status was recorded, as a localised datetime.
		"""
		return self.when_recorded.replace(tzinfo=pytz.utc).astimezone(pytz.UTC)

	def __str__(self):
		return 'Status changed to %s at %s' % (
			self.DICT_OF_STATUSES.get(self.status), self.utc_datetime
		)


class ContributionPermission(models.Model):
	PERMISSION_READ = 'read'
	PERMISSION_REPORT = 'report'
	PERMISSION_DELETE = 'delete'
	PERMISSION_EDIT = 'edit'
	PERMISSION_SMS = 'sms'
	PERMISSION_PASS = 'pass'
	PERMISSION_PAYMENT = 'payment'
	PERMISSION_REFUND = 'refund'

	OPTIONS_SETTINGS = (
		(PERMISSION_READ, 'Can read the contributions',),
		(PERMISSION_EDIT, 'Can edit the contributions',),
		(PERMISSION_REPORT, 'Can report the contribution',),
		(PERMISSION_SMS, 'Can send SMS messages about the contributions'),
		(PERMISSION_PASS, 'Can see the "print pass" button for the contribution'),
		(PERMISSION_PAYMENT, 'Can make payment for a contribution'),
		(PERMISSION_REFUND, 'Can refund a charge for a contribution'),

		(
			ContributionStatus.action_create(ContributionStatus.STATUS_APPROVED),
			'Can approve the contribution'),
		(
			ContributionStatus.action_delete(ContributionStatus.STATUS_APPROVED),
			'Can cancel approval'),
	)
	permission_name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.permission_name

	class Meta:
		db_table = 'psp_contribution_permission'

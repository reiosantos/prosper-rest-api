from django.db import models

from prosper_investments.apps.common.model_mixins import BaseModelMixin


class VenuePermission(BaseModelMixin):
	PERMISSION_READ = 'read'
	PERMISSION_REPORT = 'report'
	PERMISSION_DELETE = 'delete'
	PERMISSION_EDIT = 'edit'
	PERMISSION_SMS = 'sms'
	PERMISSION_PASS = 'pass'
	PERMISSION_PAYMENT = 'payment'
	PERMISSION_REFUND = 'refund'

	permission_name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.permission_name

	class Meta:
		db_table = 'psp_contribution_permission'

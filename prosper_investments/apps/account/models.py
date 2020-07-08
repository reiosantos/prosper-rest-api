from django.db import models

from prosper_investments.apps.account.utils import generate_account_number
from prosper_investments.apps.common.model_mixins import BaseModelMixin
from prosper_investments.apps.venue.models import User, Venue


class Account(BaseModelMixin):
	STATUS_ACTIVE = 'active'
	STATUS_CANCELLED = 'cancelled'
	STATUS_DELETED = 'deleted'
	STATUS_PENDING = 'pending'
	STATUS_DEACTIVATED = 'deactivated'

	ALLOWED_STATUS = (STATUS_ACTIVE, STATUS_CANCELLED, STATUS_DELETED, STATUS_PENDING, STATUS_DEACTIVATED)

	ACCOUNT_STATUS = (
		(STATUS_ACTIVE, 'Active'),
		(STATUS_CANCELLED, 'Cancelled'),
		(STATUS_DELETED, 'deleted'),
		(STATUS_PENDING, 'Pending Approval'),
		(STATUS_DEACTIVATED, 'Deactivated'),
	)

	account_number = models.CharField(
		max_length=20, blank=False, null=False, default=generate_account_number, unique=True)
	status = models.CharField(default=STATUS_PENDING, choices=ACCOUNT_STATUS, max_length=20)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
	current_balance = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)
	initial_balance = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)

	class Meta:
		db_table = 'psp_account'

	def __str__(self):
		return '{} - {}'.format(self.account_number, self.user)

	def delete(self, using=None, keep_parents=False):
		assert self.pk is not None, (
			"%s object can't be deleted because its %s attribute is set to None." %
			(self._meta.object_name, self._meta.pk.attname)
		)
		self.status = self.STATUS_DELETED
		self.save(update_fields=['status', 'modified_date'])
		return self


class AccountTransactions(BaseModelMixin):
	TRANSACTION_WITHDRAW = 'withdraw'
	TRANSACTION_DEPOSIT = 'deposit'
	TRANSACTION_TRANSFER = 'transfer'

	ALLOWED_TRANSACTION_TYPES = (TRANSACTION_WITHDRAW, TRANSACTION_DEPOSIT, TRANSACTION_TRANSFER)

	TRANSACTION_TYPES = (
		(TRANSACTION_WITHDRAW, 'Withdraw'),
		(TRANSACTION_DEPOSIT, 'Deposit'),
		(TRANSACTION_TRANSFER, 'Transfer'),
	)
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	operator = models.ForeignKey(
		User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teller')
	amount = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)
	previous_balance = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)
	current_balance = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)
	last_modified_by = models.ForeignKey(
		User, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_modified_by')
	transaction_type = models.CharField(default=TRANSACTION_DEPOSIT, choices=TRANSACTION_TYPES, max_length=20)
	transfer_to = models.ForeignKey(
		Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_to_account')

	class Meta:
		db_table = 'psp_account_transactions'

from django.db import models

from prosper_investments.apps.account.utils import generate_account_number
from prosper_investments.apps.common.model_mixins import BaseModelMixin
from prosper_investments.apps.venue.models import User, Venue


class Account(BaseModelMixin):
	ALLOWED_STATUS = ('active', 'cancelled', 'deleted', 'pending')
	ACCOUNT_STATUS = (
		('active', 'Active'),
		('cancelled', 'Cancelled'),
		('deleted', 'Exited / deleted'),
		('pending', 'Pending Approval'),
	)

	account_number = models.CharField(
		max_length=20, blank=False, null=False, default=generate_account_number, unique=True)
	status = models.CharField(default='pending', choices=ACCOUNT_STATUS, max_length=20)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
	current_balance = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)
	initial_balance = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)

	class Meta:
		db_table = 'psp_account'


class AccountTransactions(BaseModelMixin):
	TRANSACTION_TYPES = (
		('withdraw', 'Withdraw'),
		('deposit', 'Deposit'),
		('transfer', 'Transfer'),
	)
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	operator = models.ForeignKey(
		User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teller')
	amount = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)
	previous_balance = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)
	current_balance = models.DecimalField(decimal_places=3, default=0.0, max_digits=20)
	last_modified_by = models.ForeignKey(
		User, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_modified_by')
	transaction_type = models.CharField(default='deposit', choices=TRANSACTION_TYPES, max_length=20)
	transfer_to = models.ForeignKey(
		Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_to_account')

	class Meta:
		db_table = 'psp_account_transactions'




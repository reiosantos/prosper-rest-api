from django.contrib import admin

from prosper_investments.apps.account.models import Account


class AccountAdmin(admin.ModelAdmin):
	search_fields = ('account_number', 'user')
	fields = (
		'account_number', 'status', 'user', 'venue', 'created_date', 'modified_date'
	)
	readonly_fields = ('account_number', 'user', 'venue', 'created_date', 'modified_date')


admin.site.register(Account, AccountAdmin)

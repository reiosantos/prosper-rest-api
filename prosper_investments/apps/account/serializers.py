from django.db import transaction
from rest_framework import serializers

from prosper_investments.apps.account.models import Account


class AccountSerializer(serializers.ModelSerializer):
	class Meta:
		model = Account
		fields = '__all__'
		read_only_fields = (
			'account_number',
		)


class CreateAccountSerializer(AccountSerializer):
	def create(self, validated_data):
		user = validated_data.get('user')
		venue = self.context['request'].venue
		status = validated_data.get('status', 'pending')
		account = Account(user=user, venue=venue, status=status)

		with transaction.atomic():
			account.save()

		return account

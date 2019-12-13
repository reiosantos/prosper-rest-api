from django.db import transaction
from rest_framework import serializers

from prosper_investments.apps.account.models import Account
from prosper_investments.apps.user.serializers import UserProfileSerializer


class AccountSerializer(serializers.ModelSerializer):
	venue = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
	email = serializers.CharField(source="user.email", read_only=True)
	profile = UserProfileSerializer(source="user.profile", read_only=True)

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

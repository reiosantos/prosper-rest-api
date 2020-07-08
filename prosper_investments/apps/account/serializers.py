from django.conf import settings
from django.db import transaction
from django.urls import reverse
from rest_framework import serializers

from prosper_investments.apps.account.models import Account


class AccountSerializer(serializers.ModelSerializer):
	venue = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
	email = serializers.CharField(source="user.email", read_only=True)
	user = serializers.SerializerMethodField()

	def get_user(self, account):
		return f'{settings.PSP_BASE_URL}{reverse("user:current")}{account.user.pk}/'

	class Meta:
		model = Account
		exclude = ('id',)
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

import logging

from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from prosper_investments.apps.account.models import Account
from prosper_investments.apps.account.serializers import AccountSerializer, CreateAccountSerializer
from prosper_investments.apps.permission.permissions import AccountsView, AccountsCreate

log = logging.getLogger(__name__)


class AccountsListView(ListAPIView):
	serializer_class = AccountSerializer
	permission_classes = (IsAuthenticated, AccountsView)

	def get_queryset(self):
		return Account.objects.filter(venue=self.request.venue)


class AccountCreateView(CreateAPIView):
	serializer_class = CreateAccountSerializer
	permission_classes = (IsAuthenticated, AccountsCreate)

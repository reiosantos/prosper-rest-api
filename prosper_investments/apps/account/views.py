import logging

from django.db.models import Q
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from prosper_investments.apps.account.models import Account
from prosper_investments.apps.account.serializers import AccountSerializer, CreateAccountSerializer
from prosper_investments.apps.common.model_mixins import RetrieveUpdateDestroyViewSet
from prosper_investments.apps.permission.permissions import AccountsView, AccountsCreate

log = logging.getLogger(__name__)


class AccountsListView(ListAPIView):
	serializer_class = AccountSerializer
	permission_classes = (IsAuthenticated, AccountsView)

	def get_queryset(self):
		return Account.objects.filter(venue=self.request.venue)


class AccountsListActiveView(ListAPIView):
	serializer_class = AccountSerializer
	permission_classes = (IsAuthenticated, AccountsView)

	def get_queryset(self):
		return Account.objects.filter(venue=self.request.venue, status=Account.STATUS_ACTIVE)


class AccountsListPersonalView(ListAPIView):
	serializer_class = AccountSerializer
	permission_classes = (IsAuthenticated,)

	def get_queryset(self):
		return Account.objects.filter(
			venue=self.request.venue, user=self.request.user,  status=Account.STATUS_ACTIVE)


class AccountCreateView(CreateAPIView):
	serializer_class = CreateAccountSerializer
	permission_classes = (IsAuthenticated, AccountsCreate)


class AccountViewSet(RetrieveUpdateDestroyViewSet):
	serializer_class = AccountSerializer
	permission_classes = (IsAuthenticated, AccountsCreate)
	queryset = Account.objects.all()

	def destroy(self, request, *args, **kwargs):
		self.queryset = self.get_queryset().filter(~Q(status=Account.STATUS_DELETED))
		return super(AccountViewSet, self).destroy(request, *args, **kwargs)

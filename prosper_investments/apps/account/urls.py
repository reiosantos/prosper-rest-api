from django.urls import path

from prosper_investments.apps.account import views

app_name = 'prosper_investments.apps.account'

urlpatterns = [
	path('list/', views.AccountsListView.as_view(), name="list"),
	path('create/', views.AccountCreateView.as_view(), name="account-create"),
	path(
		'<int:pk>/',
		views.AccountViewSet.as_view(
			actions={'get': 'retrieve', 'delete': 'destroy', 'put': 'partial_update'}),
		name="account-viewset"
	),
]

from django.urls import path

from prosper_investments.apps.account import views

app_name = 'prosper_investments.apps.account'

urlpatterns = [
	path('list/', views.AccountsListView.as_view(), name="list"),
	path('create/', views.AccountCreateView.as_view(), name="account-viewset"),
]

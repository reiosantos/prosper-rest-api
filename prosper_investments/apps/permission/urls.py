from django.urls import path

from prosper_investments.apps.permission import views

app_name = 'prosper_investments.apps.permission'

urlpatterns = [
	path(
		'contribution-permission/', views.ContributionPermissionListView.as_view(),
		name='contribution-permission'),
]

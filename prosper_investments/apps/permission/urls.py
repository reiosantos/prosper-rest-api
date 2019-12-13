from django.urls import path

from prosper_investments.apps.permission import views

app_name = 'prosper_investments.apps.permission'

urlpatterns = [
	path(
		'venue-permission/', views.VenuePermissionListView.as_view(),
		name='venue-permission'),
]

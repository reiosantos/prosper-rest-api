from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from prosper_investments.apps.user import views

app_name = 'prosper_investments.apps.user'

router = DefaultRouter()
router.register('organisation', views.UsersInOrganisationViewSet, base_name='in-organisation', )
router.register('viewer-types', views.VenueViewerTypesViewSet, base_name='viewer-types', )
router.register('short/organisation', views.UsersInOrganisationShortViewSet,
                base_name='in-organisation-short', )
router.register('default/organisation', views.UsersInOrganisationDefaultPermissionViewSet,
                base_name='in-organisation-default', )

organisational_actions = views.UsersInOrganisationViewSet.as_view({
	'post': 'invite_user',
	'patch': 'change_company',
})

urlpatterns = [
	path('current/', views.CurrentUserView.as_view(), name='current'),
	path('update/', views.EditProfileView.as_view(), name='edit'),
	path('activate/', views.ActivateUserView.as_view(), name='activate'),
	path('signup/', views.CreateUserView.as_view(), name='signup'),
	path('dashboard-sections/', views.DashboardSectionsView.as_view(), name='dashboard-sections'),
	path('venue-permissions/', views.UserVenuePermissionsView.as_view(), name='dashboard-sections'),
	path('verify-exists/', views.UserExistView.as_view(), name='verify-user'),
	path('', include(router.urls))
]

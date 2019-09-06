from django.conf.urls import include
from django.urls import path
from rest_framework.routers import SimpleRouter

from prosper_investments.apps.permission import views

app_name = 'prosper_investments.apps.permission'

router = SimpleRouter()
router.register('contribution-permission', viewset=views.ContributionPermissionViewSet,
                base_name='contribution-permission')

urlpatterns = [
	path('', include(router.urls)),
]

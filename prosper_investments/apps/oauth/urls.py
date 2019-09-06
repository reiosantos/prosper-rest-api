from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from prosper_investments.apps.oauth import views

app_name = 'voyage_control.apps.oauth'

venue_token_router = DefaultRouter()
venue_token_router.register('venue_token', views.VenueTokenViewSet, base_name='venue_token')

oauth_router = DefaultRouter()
oauth_router.register('provider', views.ProviderViewSet, base_name='provider')

urlpatterns = [
	path('authorize/', views.authorize, name='authorize'),
	path('token/', views.token, name='token'),
	path('is_authenticated/', views.is_authenticated, name='is_authenticated'),

	path('', include(venue_token_router.urls)),
	path('', include(oauth_router.urls))
]

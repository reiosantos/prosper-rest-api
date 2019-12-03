from django.urls import path

from prosper_investments.apps.email import views

app_name = 'voyage_control.apps.email'

urlpatterns = [
	path('card-error/', views.CardErrorNotification.as_view(), name='card-error')
]

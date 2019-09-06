from django.urls import path

from prosper_investments.apps.terminology import views

app_name = 'voyage_control.apps.terminology'

urlpatterns = [
    path('', views.TerminologyListView.as_view(), name='list'),
]

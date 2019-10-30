from django.contrib import admin

from prosper_investments.apps.user.models import DashboardSection, VenueViewerType

admin.site.register(DashboardSection)
admin.site.register(VenueViewerType)

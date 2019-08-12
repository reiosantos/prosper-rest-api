from django.contrib import admin

from prosper_investments.apps.user.models import DashboardSection, VenueViewerType, ApiKey

admin.site.register(DashboardSection)
admin.site.register(VenueViewerType)


class ApiKeyAdmin(admin.ModelAdmin):
	list_display = ('key', 'user', 'created')
	fields = ('user',)
	ordering = ('-created',)


admin.site.register(ApiKey, ApiKeyAdmin)

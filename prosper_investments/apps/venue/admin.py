from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from prosper_investments.apps.venue.models import Venue, VenueSettingValue


class VenueSettingValueInline(admin.TabularInline):
	model = VenueSettingValue


class VenueAdmin(ImportExportModelAdmin):
	search_fields = ('name',)
	list_display = ('name', 'url_component', 'address',)
	inlines = (VenueSettingValueInline,)


admin.site.register(Venue, VenueAdmin)

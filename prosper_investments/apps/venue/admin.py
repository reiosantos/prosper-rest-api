from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from prosper_investments.apps.venue.models import Venue, VenueSettingValue, User, Role, UserData, \
	UsersVenues, UserType


class VenueSettingValueInline(admin.TabularInline):
	model = VenueSettingValue


class UserTypeInline(admin.TabularInline):
	model = UserType.venues.through


class VenueAdmin(ImportExportModelAdmin):
	search_fields = ('name',)
	list_display = ('name', 'url_component', 'address',)
	inlines = (VenueSettingValueInline,)


class UserTypeAdmin(admin.ModelAdmin):
	list_display = list_display_links = ('name',)
	list_filter = ('venues',)


admin.site.register(Venue, VenueAdmin)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(UserData)
admin.site.register(UserType, UserTypeAdmin)
admin.site.register(UsersVenues)

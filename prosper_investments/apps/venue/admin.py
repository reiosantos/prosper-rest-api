from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from prosper_investments.apps.user.models import VenueViewerType
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


class UserVenueInline(admin.TabularInline):
	model = User.venues.through


class UserAdminVenueInline(admin.TabularInline):
	model = User.admin_venues.through


class VenueViewerTypeInline(admin.TabularInline):
	model = VenueViewerType.users.through


class UserAdmin(admin.ModelAdmin):
	search_fields = ('email',)
	list_display = ('email', 'role', 'user_type',)
	fields = ('email', 'is_active', 'role', 'user_type', 'is_admin', 'date_joined', 'last_login',)
	readonly_fields = ('date_joined', 'last_login', 'created_date', 'modified_date')
	inlines = (
		VenueViewerTypeInline,
		UserAdminVenueInline,
		UserVenueInline
	)


admin.site.register(Venue, VenueAdmin)
admin.site.register(Role)
admin.site.register(User, UserAdmin)
admin.site.register(UserData)
admin.site.register(UserType, UserTypeAdmin)
admin.site.register(UsersVenues)

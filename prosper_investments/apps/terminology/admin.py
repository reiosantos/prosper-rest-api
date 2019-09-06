from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from prosper_investments.apps.terminology.models import Term, Language, Translation


class TranslationResource(resources.ModelResource):
	term = fields.Field(
		column_name='term',
		attribute='term',
		widget=ForeignKeyWidget(Term, 'key')
	)

	language = fields.Field(
		column_name='language',
		attribute='language',
		widget=ForeignKeyWidget(Language, 'code')
	)

	class Meta:
		model = Translation
		fields = (
			'id',
			'term',
			'language',
			'value',
		)


class TranslationAdmin(ImportExportModelAdmin):
	resource_class = TranslationResource

	search_fields = (
		'term__key',
		'value',
	)
	list_filter = ('language',)


admin.site.register(Term)
admin.site.register(Language)
admin.site.register(Translation, TranslationAdmin)

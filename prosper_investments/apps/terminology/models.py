from functools import reduce

from django.core.exceptions import ValidationError
from django.db import models


class Term(models.Model):
	key = models.CharField(
		max_length=150, blank=False, help_text='The key used in the front-end, e.g. `INDEX_title`')
	description = models.TextField(blank=True, help_text='Optional explanation of the key')

	def __str__(self):
		return self.key

	class Meta:
		db_table = "psp_terms"
		ordering = ('key',)


class Language(models.Model):
	code = models.CharField(max_length=10, unique=True)
	name = models.CharField(max_length=100, unique=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	class Meta:
		db_table = "psp_languages"


class TranslationManager(models.Manager):

	def values_for_venue(self, venue):
		"""
		Translations of terms, in all languages, for a venue.  The venue's
		venue-type determines the translations to use.  If there's no
		translation for a venue-type then fall back on the default translation
		(where venue-type is null).
		Args:
			venue (voyage_control.apps.legacy.models.Venue): The venue for
			which to fetch translations.

			Returns:
				(dict): A dictionary with keys being language-codes as keys, and
				values being dictionaries with terms as keys and translations
				as values.
		"""
		q = models.Q(venue__isnull=True)

		if venue:
			q |= models.Q(venue=venue)

		all_values = self.filter(q).filter(language__active=True).values(
			'term__key', 'language__code', 'value',
		)

		def values_reducer(d, row):
			language = row['language__code']
			if language not in d:
				d[language] = dict()

			language_terms = d[language]

			term = row['term__key']
			if term not in language_terms:
				language_terms[term] = row['value']

			return d

		return reduce(values_reducer, all_values, dict())

	def value_for_venue(self, key, venue):
		if venue is not None:

			filters = {
				'term__key': key,
				'language__code': venue.language_code
			}
			translation = self.filter(venue=venue, **filters).order_by('id').first()
			if translation and translation.value:
				return translation.value

			translation = self.filter(**filters).order_by('id').first()
			if translation and translation.value:
				return translation.value
		return key


class Translation(models.Model):
	term = models.ForeignKey(Term, on_delete=models.CASCADE)
	language = models.ForeignKey(Language, on_delete=models.CASCADE)
	value = models.TextField()
	venue = models.ForeignKey('venue.Venue', blank=True, null=True, on_delete=models.SET_NULL)

	objects = TranslationManager()

	class Meta:
		db_table = "psp_translations"
		unique_together = (
			('venue', 'term', 'language',),
		)

		ordering = (
			'term__key',
			'language__code',
		)

	def save(self, *args, **kwargs):
		"""
		Ensures uniqueness of translations for null venue-type.
		"""
		conflicting_instance = Translation.objects.filter(
			term=self.term,
			language=self.language,
			venue__isnull=True
		)

		if self.pk:
			conflicting_instance = conflicting_instance.exclude(pk=self.pk)

		if conflicting_instance.exists():
			raise ValidationError({
				'error':
					'Generic translation for this term (%s) and language (%s) already exists.' % (
						self.term, self.language
					)
			})

		super(Translation, self).save(*args, **kwargs)

	def __str__(self):
		name = u'%s in %s' % (self.term, self.language,)

		if self.venue:
			name = u'%s at %s' % (name, self.venue)

		return name

from rest_framework import serializers

from prosper_investments.apps.terminology.models import Translation


class TranslationSerializer(serializers.ModelSerializer):
	term = serializers.CharField()

	language = serializers.CharField()

	class Meta:
		model = Translation
		fields = (
			'term',
			'language',
			'value',
		)

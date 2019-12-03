from rest_framework import serializers


class TimeField(serializers.SlugRelatedField):
	def to_representation(self, obj):
		return obj.__str__()

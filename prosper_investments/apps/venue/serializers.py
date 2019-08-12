from datetime import datetime

from rest_framework import serializers

from prosper_investments.apps.venue.models import VenueSettingValue, Venue


class VenueSettingValueSerializer(serializers.ModelSerializer):
	path = serializers.CharField(source='setting.var_define')

	class Meta:
		model = VenueSettingValue
		fields = ('path', 'value')

	def update(self, instance, validated_data):
		instance.value = validated_data['value']
		instance.save()
		return instance


class ListVenueSerializer(serializers.ModelSerializer):
	settings = VenueSettingValueSerializer(source='setting_values', many=True, read_only=True)
	timezone = serializers.SerializerMethodField()
	offset = serializers.SerializerMethodField()
	url = serializers.CharField(source='rest_api_url')

	class Meta:
		model = Venue
		fields = ('id', 'url_component', 'name', 'active', 'timezone', 'offset', 'settings', 'url')

	def get_timezone(self, obj):
		return obj.local_timezone.zone

	def get_offset(self, obj):
		return datetime.now(obj.local_timezone).strftime('%z')

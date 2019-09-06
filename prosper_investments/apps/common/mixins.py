from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN, \
	LOOKUP_QUERY_GT, LOOKUP_QUERY_GTE, LOOKUP_QUERY_LT, LOOKUP_QUERY_LTE
from django_elasticsearch_dsl_drf.filter_backends import FilteringFilterBackend, \
	OrderingFilterBackend, CompoundSearchFilterBackend
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet


class ElasticSearchMixin(DocumentViewSet):
	lookup_field = 'id'

	# Define search fields
	filter_backends = [
		FilteringFilterBackend,
		OrderingFilterBackend,
		# DefaultOrderingFilterBackend,
		CompoundSearchFilterBackend
	]
	# Filter fields
	filter_fields = {
		'id': {
			'field': 'id',
			'lookups': [
				LOOKUP_FILTER_RANGE,
				LOOKUP_QUERY_IN,
				LOOKUP_QUERY_GT,
				LOOKUP_QUERY_GTE,
				LOOKUP_QUERY_LT,
				LOOKUP_QUERY_LTE,

			]
		},
		'created': 'created',
		'modified': 'modified',
	}
	# Define ordering fields
	ordering_fields = {
		'id': 'id',
		'created': 'created',
		'modified': 'modified',
		'pub_date': 'pub_date',
	}
	# Specify default ordering
	ordering = ('id', 'created',)

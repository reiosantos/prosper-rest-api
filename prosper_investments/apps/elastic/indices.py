from django_elasticsearch_dsl import Index

venue_index = Index('venues')
venue_index.settings(
	number_of_shards=1,
	number_of_replicas=1
)

user_index = Index('users')
user_index.settings(
	number_of_shards=1,
	number_of_replicas=2
)

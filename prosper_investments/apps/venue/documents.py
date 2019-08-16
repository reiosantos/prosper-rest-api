from django_elasticsearch_dsl import Index, fields
from django_elasticsearch_dsl.documents import DocType
from elasticsearch_dsl import analyzer

from prosper_investments.apps.venue.models import User

venue_index = Index('venues')
venue_index.settings(
	number_of_shards=1,
	number_of_replicas=0
)
html_strip = analyzer(
	'html_strip',
	tokenizer="standard",
	filter=["standard", "lowercase", "stop", "snowball"],
	char_filter=["html_strip"]
)


@venue_index.doc_type
class UserDocument(DocType):
	id = fields.IntegerField(
		analyzer=html_strip,
		fields={
			'raw': fields.StringField(analyzer='keyword')
		}
	)
	email = fields.TextField(
		analyzer=html_strip,
		fields={
			'raw': fields.StringField(analyzer='keyword')
		}
	)
	is_active = fields.BooleanField()
	date_joined = fields.DateField()
	is_admin = fields.BooleanField()

	class Django:
		model = User

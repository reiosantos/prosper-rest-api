from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.documents import DocType
from elasticsearch_dsl import analyzer

from prosper_investments.apps.elastic.indices import user_index
from prosper_investments.apps.venue.models import User

html_strip = analyzer(
	'html_strip',
	tokenizer="standard",
	filter=["standard", "lowercase", "stop", "snowball"],
	char_filter=["html_strip"]
)


@user_index.doc_type
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
	profile = fields.ObjectField()
	full_name = fields.TextField()
	is_active = fields.BooleanField()
	date_joined = fields.DateField()
	is_admin = fields.BooleanField()

	class Django:
		model = User

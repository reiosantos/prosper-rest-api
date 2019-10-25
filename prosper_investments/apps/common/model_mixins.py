from django.db import models


class BaseModelMixin(models.Model):
	created_date = models.DateTimeField(auto_now=True, editable=False)
	modified_date = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

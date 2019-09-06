from django.db import models


class UpperCaseCharField(models.CharField):
	"""
	Upper-case char-field.  Before being written to the database, the contents
	of this field gets upper-cased.
	"""

	def __init__(self, *args, **kwargs):
		super(UpperCaseCharField, self).__init__(*args, **kwargs)

	def pre_save(self, model_instance, add):
		value = getattr(model_instance, self.attname, None)
		if value:
			value = value.upper()
			setattr(model_instance, self.attname, value)
			return value
		else:
			return super(UpperCaseCharField, self).pre_save(model_instance, add)


class LowerCaseCharField(models.CharField):
	"""
	Lower-case char-field.  Before being written to the database, the contents
	of this field gets lower-cased.
	"""

	def __init__(self, *args, **kwargs):
		super(LowerCaseCharField, self).__init__(*args, **kwargs)

	def pre_save(self, model_instance, add):
		value = getattr(model_instance, self.attname, None)
		if value:
			value = value.lower()
			setattr(model_instance, self.attname, value)
			return value
		else:
			return super(LowerCaseCharField, self).pre_save(model_instance, add)

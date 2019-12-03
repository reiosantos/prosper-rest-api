import collections
import logging

import re

logger = logging.getLogger(__name__)


def validate_date_range_venue(value):
	date_range = value.split(',')
	if len(date_range) != 2:
		return False
	else:
		try:
			from_date = int(date_range[0])
			to_date = int(date_range[1])
			if from_date > to_date:
				return False
		except Exception as e:
			logger.error("Error: %s" % e)
			return False
	return True


class SimulatedObject:
	object_name = None
	ref = None
	skip_props = None

	def __init__(self, obj):
		self.ref = obj
		properties = [prop for prop in dir(obj) if not (prop.startswith('_') or prop[
			0].isupper() or prop in self.skip_props)]
		for prop in properties:
			try:
				setattr(self, prop, getattr(obj, prop))
			except Exception as err:
				logger.exception(str(err))


def convert_to_python_date_string_format(string):
	"""Converts angular/php date time string format to python string format"""

	values = collections.OrderedDict([
		('yyyy', '%Y'),
		('yy', '%y'),
		('MMMM', '%B'),
		('MMM', '%b'),
		('MM', '%m'),
		('dd', '%d'),
		('HH', '%H'),
		('hh', '%I'),
		('h', '%I'),
		('a', '%p'),
		('mm', '%M'),
		('ss', '%S'),
		('EEEE', '%A'),
		('EEE', '%a'),
		('ww', '%W'),
		('Z', '%z'),
	])

	for word, initial in values.items():
		src_str = re.compile(word)
		string = src_str.sub(initial, string)

	return string


"""
FIELD_REQUIREMENT_CHOICES is used to define if a field is either hidden (not used) in frontend, 
optional (used but can
be empty) or mandatory (required field)
"""
FIELD_REQUIREMENT_CHOICES = (
	(0, 'Hidden'),
	(1, 'Optional'),
	(2, 'Mandatory'),
)


def field_hidden():
	return FIELD_REQUIREMENT_CHOICES[0][0]


def field_optional():
	return FIELD_REQUIREMENT_CHOICES[1][0]


def field_mandatory():
	return FIELD_REQUIREMENT_CHOICES[2][0]

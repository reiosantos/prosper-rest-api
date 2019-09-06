import re
from collections import OrderedDict

first_cap_re = re.compile(r'(.)([A-Z][a-z]+)')
all_cap_re = re.compile(r'([a-z0-9])([A-Z])')

"""
Methods ported from djangorestframework-camel-case.util
"""


# noinspection PyPep8Naming
def underscoreToCamel(match):
	return match.group()[0] + match.group()[2].upper()


def camelize(data):
	if isinstance(data, dict):
		new_dict = OrderedDict()
		for key, value in data.items():
			new_key = re.sub(r"[a-z]_[a-z]", underscoreToCamel, key)
			new_dict[new_key] = camelize(value)
		return new_dict
	if isinstance(data, (list, tuple)):
		for i in range(len(data)):
			data[i] = camelize(data[i])
		return data
	return data


def camel_to_underscore(name):
	s1 = first_cap_re.sub(r'\1_\2', name)
	return all_cap_re.sub(r'\1_\2', s1).lower()


def underscoreize(data):
	if isinstance(data, dict):
		new_dict = {}
		for key, value in data.items():
			new_key = camel_to_underscore(key)
			new_dict[new_key] = underscoreize(value)
		return new_dict
	if isinstance(data, (list, tuple)):
		for i in range(len(data)):
			data[i] = underscoreize(data[i])
		return data
	return data


"""
Custom methods utilizing camel-case
"""


def camel_case(snake_case):
	return re.sub(r"[a-z]_[a-z]", underscoreToCamel, snake_case)


def camelcasefield(field):
	try:
		splitted = field.split('_')
		sub_splitted = [(word[:1].upper(), word[1:]) for word in splitted[1:]]
		splitted = splitted[:1] + ["".join(word) for word in sub_splitted]
		return "".join(splitted)
	except ValueError:
		return field


def snake_case(name):
	s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
	return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

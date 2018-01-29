try:
	import ujson as json
except ImportError:
	import json

import six


class JsonSerializable:
	"""
	Subclasses of this class are guaranteed to be able to be converted to JSON format.
	All subclasses of this class must override to_json.
	"""

	def to_json(self):
		"""
		Returns a JSON string representation of this class.

		This function must be overridden by subclasses.
		:return: a JSON formatted string.
		"""
		raise NotImplementedError


class Dictionaryable:
	"""
	Subclasses of this class are guaranteed to be able to be converted to dictionary.
	All subclasses of this class must override to_dic.
	"""

	def to_dic(self):
		"""
		Returns a JSON string representation of this class.

		This function must be overridden by subclasses.
		:return: a JSON formatted string.
		"""
		raise NotImplementedError


class JsonDeserializable:
	"""
	Subclasses of this class are guaranteed to be able to be created from a json-style dict or json formatted string.
	All subclasses of this class must override de_json.
	"""

	@classmethod
	def de_json(cls, json_type):
		"""
		Returns an instance of this class from the given json dict or string.

		This function must be overridden by subclasses.
		:return: an instance of this class created from the given json dict or string.
		"""
		raise NotImplementedError

	@staticmethod
	def check_json(json_type):
		"""
		Checks whether json_type is a dict or a string. If it is already a dict, it is returned as-is.
		If it is not, it is converted to a dict by means of json.loads(json_type)
		:param json_type:
		:return:
		"""
		try:
			str_types = (str, unicode)
		except NameError:
			str_types = (str,)

		if type(json_type) == dict:
			return json_type
		elif type(json_type) in str_types:
			return json.loads(json_type)
		else:
			raise ValueError("json_type should be a json dict or string.")

	def __str__(self):
		d = {}
		for x, y in six.iteritems(self.__dict__):
			if hasattr(y, '__dict__'):
				d[x] = y.__dict__
			else:
				d[x] = y

		return six.text_type(d)


class KeyboardAction(JsonSerializable, Dictionaryable):

	def to_dict(self):
		return {"type": "imBack", 'title': self.title, 'value': self.value}

	def to_json(self):
		return json.dumps(self.to_dict())

	def __init__(self, title, value):
		self.title = title
		self.value = value


class Keyboard(JsonSerializable, Dictionaryable):

	def to_dict(self):
		json_dict = {
			"actions": []
		}
		if self.actions:
			for ac in self.actions:
				json_dict['actions'].append(ac.to_dict())

		return json_dict

	def to_json(self):

		return json.dumps(self.to_dict())

	def __init__(self, *actions):
		self.actions = actions

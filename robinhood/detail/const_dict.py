import pprint

class ConstDict:
	def __init__(self, dictionary: dict):
		self._dict = dictionary

	def keys(self):
		return self._dict.keys()

	def values(self):
		return self._dict.values()

	def items(self):
		return self._dict.items()

	def __getitem__(self, item):
		return self._dict[item]

	def __contains__(self, item):
		return self._dict.__contains__(item)

	def __str__(self):
		return pprint.pformat(self._dict)

	def __repr__(self):
		return self.__str__()
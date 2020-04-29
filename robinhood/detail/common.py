import pandas as pd
import pprint
from datetime import datetime
from dateutil import parser

class PrettyDict:
	def __init__(self, dict):
		self._dict = dict

	def __getattr__(self, key):
		return self._dict.__getattr__(key)

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return pprint.pformat(self._dict)


def timestamp_now():
	return pd.Timestamp.now()


def _to_float(value):
	if value:
		return float(value)
	else:
		return value


def _make_query_string(json: dict):
	if not any(json.values()):
		return ''
	else:
		return '?' + '&'.join(f'{k}={v}' for k, v in json.items() if v)


def _datelike_to_datetime(date: [int, str, datetime], default=None):
	if not date:
		return default

	if isinstance(date, datetime):
		return date

	if isinstance(date, int):
		date = str(date)

	if isinstance(date, str):
		if date.isnumeric() and len(date) == len('yyyymmdd'):
			return datetime.strptime(str(date), '%Y%m%d')
		else:
			return parser.parse(date)

	raise Exception("Unable to detect format of : " + str(date))
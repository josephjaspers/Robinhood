import pandas as pd


def timestamp_now():
	return pd.Timestamp.now()


def _to_float(value):
	if value:
		return float(value)
	else:
		return value

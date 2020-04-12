from .detail.const_dict import ConstDict
from .detail.common import timestamp_now, _to_float
from datetime import datetime
import pandas as pd


class QuoteBase(ConstDict):

	def __init__(self, quote):
		quote['time'] = timestamp_now()
		ConstDict.__init__(self, quote)

	def _get(self, key):
		return self._dict[key]

	def _get_float(self, key):
		return _to_float(self._get(key))

	@property
	def symbol(self) -> str:
		return self._dict['symbol']

	@property
	def time(self) -> pd.Timestamp:
		return self._dict['time']


class Quote(QuoteBase):
	"""
	Example json quote
		{
			"ask_price":"253.810000",
			"ask_size":144,
			"bid_price":"253.510000",
			"bid_size":100,
			"last_trade_price":"254.290000",
			"last_extended_hours_trade_price":"253.500000",
			"previous_close":"254.810000",
			"adjusted_previous_close":"254.810000",
			"previous_close_date":"2020-03-30",
			"symbol":"AAPL",
			"trading_halted":"False",
			"has_traded":"True",
			"last_trade_price_source":"consolidated",
			"updated_at":"2020-03-31T21:27:45Z",
			"instrument":"https://api.robinhood.com/instruments/450dfc6d-5510-4d40-abfb-f633b7d9be3e/"
		}
	"""

	@property
	def ask(self) -> float:
		return self._get_float('ask_price')

	def __init__(self, quote):
		QuoteBase.__init__(self, quote)

	@property
	def bid(self) -> float:
		return self._get_float('bid_price')

	@property
	def mark(self) -> float:
		return self._get_float('last_trade_price')

	@property
	def last_trade_price(self) -> float:
		return self._get_float('last_trade_price')

	@property
	def previous_close(self) -> float:
		return self._get_float('last_trade_price')

	@property
	def adjusted_previous_close(self) -> float:
		return self._get_float('last_trade_price')

	@property
	def ask_size(self) -> int:
		return self._dict['ask_size']

	@property
	def bid_size(self) -> int:
		return self._dict['bid_size']


class CryptoQuote(QuoteBase):
	"""
	Example json quote
		{
		   "ask_price":"6457.583965",
		   "bid_price":"6449.317366",
		   "mark_price":"6453.450665",
		   "high_price":"6539.245000",
		   "low_price":"6319.569798",
		   "open_price":"6441.625000",
		   "symbol":"BTCUSD",
		   "id":"3d961844-d360-45fc-989b-f6fca761d511",
		   "volume":"0.000000"   ##Note Rb currently always returns volume being 0
		}
	"""

	def __init__(self, quote):
		QuoteBase.__init__(self, quote)

	@property
	def ask(self) -> float:
		return self._get_float('ask_price')

	@property
	def bid(self) -> float:
		return self._get_float('bid_price')

	@property
	def mark(self) -> float:
		return self._get_float('mark_price')

	@property
	def high(self) -> float:
		return self._get_float('high_price')

	@property
	def low(self) -> float:
		return self._get_float('low_price')

	@property
	def open(self) -> float:
		return self._get_float('open_price')
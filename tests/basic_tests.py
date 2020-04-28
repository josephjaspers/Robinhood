import unittest
from unittest import TestCase

from ...robinhood import Trader
from ...robinhood.robinhood.order import Order, CryptoOrder
from ...robinhood.robinhood.quote import Quote, CryptoQuote


class TestAll(TestCase):

	# basic tests to ensure the endpoints work

	def __init__(self, *args, **kwargs):
		self.trader = Trader()
		self.trader.login()  # will supply console prompt
		TestCase.__init__(self, *args, **kwargs)

	def test_fundamentals(self):
		f = self.trader.fundamentals('aapl')
		assert(isinstance(f, dict))

	def test_instrument(self):
		i = self.trader.instrument('aapl')
		assert(isinstance(i, dict))

	def test_quote(self):
		q = self.trader.quote('aapl')
		assert(isinstance(q, Quote))

		data = [
			q.ask,
			q.bid,
			q.adjusted_previous_close,
			q.last_trade_price,
			q.previous_close
		]
		assert all([isinstance(value, float) for value in data])

		q = self.trader.quote('btc')
		assert isinstance(q, CryptoQuote)
		data = [
			q.ask,
			q.bid,
			q.mark
		]
		assert all([isinstance(value, float) for value in data])

	def test_orders(self):
		os = self.trader.orders()
		assert all([isinstance(order, Order) for order in os])

		os = self.trader.crypto_orders()
		assert all([isinstance(order, CryptoOrder) for order in os])

	def test_account_data(self):
		funcs = ['account',
				'crypto_account',
				'portfolio',
				'orders',
				'crypto_orders',
				'dividends',
				'positions']

		for str_func in funcs:
			function = getattr(self.trader, str_func)

	#  TODO -- add testing for buying or selling
	#  Maybe only test limit orders to avoid execution?

	def test_historical_data(self):
		quotes = self.trader.historical_quotes('aapl')
		assert(len(quotes) > 10)  # length will be in 100s

		historical_quote = quotes[0]
		# test properties
		high = historical_quote.high
		low = historical_quote.low
		close = historical_quote.close
		open = historical_quote.open
		time = historical_quote.time

		import pandas as pd
		assert (isinstance(time, pd.Timestamp))
		assert(low < high)


if __name__ == '__main__':
	unittest.main()

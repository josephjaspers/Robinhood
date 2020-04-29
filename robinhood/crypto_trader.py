from . import crypto_endpoints
from .crypto_endpoints import crypto_pairs as _crypto_pairs
from .order import CryptoOrder
from .quote import CryptoQuote, HistoricalQuote
import uuid
from json import dumps
import pandas as pd

class CryptoTrader:

	def __init__(self, trader):
		self.trader = trader

	@property
	def _req_post(self):
		return self.trader._req_post

	@property
	def _req_get(self):
		return self.trader._req_get

	@property
	def _fprice(self):
		return self.trader._fprice

	def quote(self, symbol):
		json = self._req_get(crypto_endpoints.quotes(symbol))
		return CryptoQuote(json)

	def historical_quotes(self,
						  symbol,
						  interval,
						  span=None,
						  start=None,
						  stop=None,
						  bounds='24_7'):
		return self.trader.historical_quotes(
			symbol=symbol,
			interval=interval,
			span=span,
			start=start,
			stop=stop,
			bounds=bounds,
			_json_key='data_points',
			_endpoint=crypto_endpoints
		)

	def account(self):
		res = self._req_get(crypto_endpoints.accounts())
		return res['results'][0]

	def orders(self):
		orders = self._req_get(crypto_endpoints.orders())['results']
		return [CryptoOrder(self, order, False) for order in orders]

	def order(self, order):
		order_id = order['id'] if isinstance(order, dict) else order
		json = self._req_get(crypto_endpoints.orders() + order_id)
		return CryptoOrder(self, json, False)

	def buy(self,
		    symbol,
		    price_quantity=None,
		    quantity=None,
		    price=None,
		    time_in_force=None):
		"""
		Args:
			price_quantity: Buy an amount of bitcoin equal to this dollar amount
			symbol: the stock symbol
			quantity: number of shares
			price: the limit price, if None defaults to a market order
			time_in_force: 'gfd' or 'gtc', gfd: cancel end of day, gtc: cancel until specified

		Returns: CryptoOrder object
		"""
		return self.place_order(symbol=symbol,
									   price_quantity=price_quantity,
									   quantity=quantity,
									   price=price,
									   side='buy',
									   time_in_force=time_in_force)

	def sell(self,
			symbol,
			price_quantity=None,
			quantity=None,
			price=None,
			time_in_force=None):
		"""
		Args:
			price_quantity: Sell an amount of bitcoin equal to this dollar amount
			symbol: the stock symbol
			quantity: number of shares
			price: the limit price, if None defaults to a market order
			time_in_force: 'gfd' or 'gtc', gfd: cancel end of day, gtc: cancel until specified

		Returns: CryptoOrder object
		"""
		return self.place_order(symbol=symbol,
									   price_quantity=price_quantity,
									   quantity=quantity,
									   price=price,
									   side='sell',
									   time_in_force=time_in_force)

	def place_order(self,
				   symbol,
				   price_quantity,
				   quantity=None,
				   price=None,
				   side=None,
				   time_in_force=None):
		assert bool(quantity) ^ bool(price_quantity)
		symbol = symbol.upper()
		order = 'limit' if price else 'market'
		crypto_id = _crypto_pairs[symbol]

		if not time_in_force: time_in_force = 'gtc'
		if not price: price = self.quote(symbol).ask
		if not quantity and price_quantity:
			quantity = "{0:.6f}".format(price_quantity / price)

		price = self._fprice(price)
		account_id = self.account()['id']

		payload = {
			"type": order,
			"side": side,
			"quantity": quantity,
			"account_id": account_id,
			"currency_pair_id": crypto_id,
			'price': price,
			'ref_id': uuid.uuid4().hex,
			"time_in_force": time_in_force
		}

		payload = {k: v for k, v in payload.items() if v}
		payload = dumps(payload)
		json = self._req_post(crypto_endpoints.orders(), data=payload)
		return CryptoOrder(self, json)

	@property
	def cancel(self):
		return self.trader.cancel
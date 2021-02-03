from .detail.const_dict import ConstDict
from .detail.common import timestamp_now, _to_float
from datetime import datetime
from .common.ticker import Ticker

class OrderBase(ConstDict):
	def __init__(self, order: dict, init_local_time=True):
		if init_local_time:
			order['time'] = timestamp_now()
		ConstDict.__init__(self, order)

	@property
	def time(self) -> datetime:
		return self._dict['time'] if 'time' in self._dict else None


class Order(OrderBase):
	"""
	Example json:
	{
		ref_id: "182f1587-0dbd-4b22-910c-e670e38b8774"
		account: "https://api.robinhood.com/accounts/{account_id}/"
		instrument: "https://api.robinhood.com/instruments/guid/"
		symbol: "GRPN"
		quantity: "1"
		side: "sell"
		type: "market"
		trigger: "stop"
		time_in_force: "gfd"
		extended_hours: false
		stop_price: "0.74"
		trailing_peg: {
			type: "percentage"
			percentage: "15"
		}
	}
	"""

	def __init__(self, trader, order: dict, init_local_time=True):
		OrderBase.__init__(self, order, init_local_time)
		self._trader = trader
		self.__trailing_stoploss_max_price = self.price #not always used
		self.__trailing_stoploss_percent = None

	def update(self):
		"""Update this order's information by pinging robinhood"""
		update_dict = self._trader.order(self._dict)._dict

		# historical orders will not have time,
		# orders made during this session will have a pd.Timestamp added to them
		if 'time' in self:
			update_dict['time'] = self.time

		self._dict = update_dict

	def cancel(self):
		"""Cancel this order, does not check if ordered has been executed"""
		return self._trader.cancel(self)

	def filled(self, update=True):
		"""Updates self and checks if the order has been filled"""
		return self.status(update) == 'filled'

	def canceled(self, update=True):
		"""Updates self and checks if the order has been cancelled"""
		return self.status(update) in ['cancelled', 'canceled']

	def is_open(self, update=True):
		return self.status(update) not in ['cancelled', 'canceled', 'filled']

	def status(self, update=True):
		"""Returns state of order, return values are 'filled', 'cancelled', 'pending', 'queued'?"""
		status = self._dict['state']
		if update and status not in ['cancelled', 'canceled', 'filled']:
			self.update()
			status = self._dict['state']
		return status

	@property
	def price(self) -> float:
		return _to_float(self._dict['price'])

	@property
	def side(self) -> str:
		return self._dict['side']

	@property
	def quantity(self) -> int:
		return self._dict['quantity']

	def add_stop_loss(self, percent, poll_rate_seconds=60):
		from threading import Thread
		if (self.side != 'buy'):
			raise Exception("add_stop_loss must be called on a buy-order")

		thread = Thread(target=self._poll_for_stoploss, args=[percent, poll_rate_seconds])
		setattr(self, '__max_price_since_order', self.price)
		thread.run()

	def _poll_for_stoploss(self, percent, poll_rate_seconds):

		def __sell_off():
			self._trader.sell(self.symbol, quantity=self.quantity)

		ticker = Ticker(poll_rate_seconds)
		relative_percent = 1 - percent

		while True:
			if ticker.tick():
				self.update()
				if self.filled():
					quote = self._trader.quote(self.symbol)
					price = quote.price
					if self.__trailing_stoploss_max_price < price:
						self.__trailing_stoploss_max_price = price
					elif price < self.__stoploss_max_price * relative_percent:
						__sell_off()
						return

				if self.canceled():
					return

class CryptoOrder(Order):
	"""
	Example json:
	{
		'account_id': '<account_id>>',
		'average_price': None,
		'cancel_url': 'https://nummus.robinhood.com/orders/<cancel_url>/cancel/',
		'created_at': '2020-04-01T13:14:07.696296-04:00',
		'cumulative_quantity': '0.000000000000000000',
		'currency_pair_id': '3d961844-d360-45fc-989b-f6fca761d511',
		'executions': [],
		'id': '<guid>',
		'last_transaction_at': None,
		'price': '6194.960000000000000000',
		'quantity': '0.000018220000000000',
		'ref_id': '<guid>>',
		'rounded_executed_notional': '0.00',
		'side': 'buy',
		'state': 'unconfirmed',
		'time_in_force': 'gtc',
		'type': 'market',
		'updated_at': '2020-04-01T13:14:07.785202-04:00'
	}
	"""

	def update(self):
		# TODO- can we find a way to query a single crypto-order?
		order_id = self._dict['id']
		orders = self._trader.orders()
		crypto_order = next(order for order in orders if order['id'] == order_id)
		update_dict = crypto_order._dict
		if self.time:
			update_dict['time'] = self.time

		self._dict = update_dict

	def status(self, update=True):
		if update:
			self.update()
		return self._dict['state']

	@property
	def quantity(self) -> float:
		return float(self._dict['quantity'])
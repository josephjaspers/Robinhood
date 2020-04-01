from .detail.const_dict import ConstDict
from datetime import datetime


class OrderBase(ConstDict):
	def __init__(self, order: dict):
		order['time'] = datetime.now()

		# TODO add `quantity` when fractional shares are supported
		for key in ['price', 'stop_price']:
			if key in order and order[key]:
				order['price'] = float(order[key])
			ConstDict.__init__(self, order)

	@property
	def time(self) -> datetime:
		return self._dict['time']


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

	def __init__(self, trader, order: dict):
		OrderBase.__init__(self, order)
		self._trader = trader

	def update(self):
		"""Update this order's information by pinging robinhood"""
		self._dict = self._trader.order(self._dict)

	def cancel(self):
		"""Cancel this order, does not check if ordered has been executed"""
		return self._trader.cancel(self)

	def filled(self, update=True):
		"""Updates self and checks if the order has been filled"""
		return self.status(update) == 'filled'

	def canceled(self, update=True):
		"""Updates self and checks if the order has been canceled"""
		return self.status(update) == 'canceled'

	def status(self, update=True):
		"""Returns state of order, return values are 'filled', 'canceled', 'pending', 'queued'?"""
		status = self._dict['status']
		if update and status not in ['canceled', 'filled']:
			self.update()
			status = self._dict['status']
		return status

	@property
	def price(self) -> float:
		return self._dict['price']

	@property
	def side(self) -> str:
		return self._dict['side']

	@property
	def quantity(self) -> int:
		return self._dict['quantity']


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
		orders = self._trader.crypto_orders()
		self._dict = next(order for order in orders if order['id'] == order_id)

	def status(self, update=True):
		if update:
			self.update()
		return self._dict['state']

	@property
	def price(self) -> float:
		return self._dict['price']

	@property
	def side(self) -> str:
		return self._dict['side']

	@property
	def quantity(self) -> float:
		return self._dict['quantity']
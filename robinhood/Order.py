class Order:

	def __init__(self, trader, order: dict):
		self.order = order
		self.trader = trader

	def __getitem__(self, item):
		return self.order[item]

	def __contains__(self, item):
		return self.order.__contains__(item)

	def update(self):
		self.order = self.trader.order(self.order)

	def cancel(self):
		return self.trader.cancel(self)

	def filled(self):
		self.update()
		return self.order['status'] == 'filled'

	def canceled(self):
		self.update()
		return self.order['status'] == 'canceled'

	def __repr__(self):
		return self.order.__repr__()

	def __str__(self):
		return self.order.__str__()


class CryptoOrder(Order):

	def update(self):
		# TODO- can we find a way to query a single crypto-order?
		order_id = self.order['id']
		orders = self.trader.crypto_orders()
		self.order = next(order for order in orders if order['id'] == order_id)

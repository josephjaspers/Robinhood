crypto_base_url = 'https://nummus.robinhood.com/'

crypto_pairs = {
	'BTCUSD': '3d961844-d360-45fc-989b-f6fca761d511',
	'ETHUSD': '76637d50-c702-4ed1-bcb5-5b0732a81f48',
	'ETCUSD': '7b577ce3-489d-4269-9408-796a0d1abb3a',
	'BCHUSD': '2f2b77c4-e426-4271-ae49-18d5cb296d3a',
	'BSVUSD': '086a8f9f-6c39-43fa-ac9f-57952f4a1ba6',
	'LTCUSD': '383280b1-ff53-43fc-9c84-f01afd0989cd',
	'DOGEUSD': '1ef78e1b-049b-4f12-90e5-555dcf2fe204'
}


def orders():
	return crypto_base_url + 'orders/'


def accounts():
	return crypto_base_url + 'accounts/'


def cancel_order(order_id):
	"""POST ME"""
	return f"https://nummus.robinhood.com/orders/{order_id}/cancel/"


def quotes(symbol):
	return f'https://api.robinhood.com/marketdata/forex/quotes/{symbol}/'


def portfolios(account=None):
	return crypto_base_url + 'portfolios/' + (account if account else '')

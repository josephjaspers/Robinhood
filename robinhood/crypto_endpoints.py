from .detail.common import _make_query_string
crypto_base_url = 'https://nummus.robinhood.com/'

crypto_pairs = {
	'BTC': '3d961844-d360-45fc-989b-f6fca761d511',
	'ETH': '76637d50-c702-4ed1-bcb5-5b0732a81f48',
	'ETC': '7b577ce3-489d-4269-9408-796a0d1abb3a',
	'BCH': '2f2b77c4-e426-4271-ae49-18d5cb296d3a',
	'BSV': '086a8f9f-6c39-43fa-ac9f-57952f4a1ba6',
	'LTC': '383280b1-ff53-43fc-9c84-f01afd0989cd',
	'NEO': 'b9729798-2aec-4ca9-8637-4d9789d63764',
	'OMG': 'bab5ccb4-6729-416e-ac75-019d650016c9',
	'LSK': '2de36458-56cf-458d-b76a-6b3f61b2034c',
	'BTG': 'a31d3fe3-38e6-4adf-ab4b-e303349f5ee4',
	'DASH': '1461976e-a656-481a-af27-dc6f2980e967',
	'XMR': 'cc2eb8d1-c42d-4f12-8801-1c4bbe43a274',
	'ZEC': '35f0496d-6c3a-4cac-9d2f-6702a8c387eb',
	'XLM': '7a04fe7a-e3a8-4a07-8c35-d0fec9f35569',
	'QTUM': '7837d558-0fe9-4287-8f3e-6de592db127c',
	'XRP': '5f1325b6-f63c-4367-9d6f-713e3a0c5d76',
	'DOGE': '1ef78e1b-049b-4f12-90e5-555dcf2fe204'
}


def orders():
	return crypto_base_url + 'orders/'


def accounts():
	return crypto_base_url + 'accounts/'


def cancel_order(order_id):
	"""POST ME"""
	return crypto_base_url + f"/orders/{order_id}/cancel/"


def quotes(symbol):
	crypto_id = crypto_pairs[symbol.upper()]
	return f'https://api.robinhood.com/marketdata/forex/quotes/{crypto_id}/'


def historical_quotes(symbol,**kwargs):
	crypto_id = crypto_pairs[symbol.upper()]
	url = f'https://api.robinhood.com/marketdata/forex/historicals/{crypto_id}/'
	url += _make_query_string(kwargs)
	return url


def portfolios(account=None):
	return crypto_base_url + 'portfolios/' + (account if account else '')

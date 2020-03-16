crypto_base_url = 'https://nummus.robinhood.com/'


def _fix_symbol(symbol:str):
	symbol = symbol.upper()
	return symbol if symbol.endswith('USD') else symbol + 'USD'


def orders():
	return 'https://nummus.robinhood.com/orders/'


def quotes(symbol):
	return f'https://api.robinhood.com/marketdata/forex/quotes/{_fix_symbol(symbol)}/'

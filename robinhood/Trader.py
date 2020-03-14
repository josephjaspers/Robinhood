import warnings
from six.moves.urllib.request import getproxies
from six.moves import input

import getpass
import requests
import dateutil
import uuid
import pickle

from . import exceptions as RH_exception
from . import endpoints
from .enums import Transaction, Bounds


class Trader:
    """Wrapper class for fetching/parsing robinhood endpoints """
    session = None
    headers = None
    auth_token = None
    refresh_token = None
    current_device_token = None

    client_id = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"

    ###########################################################################
    #                       Logging in and initializing
    ###########################################################################

    def __init__(self):
        self.session = requests.session()
        self.session.proxies = getproxies()
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-robinhood-API-Version": "1.265.0",
            "Connection": "keep-alive",
            "User-Agent": "robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        }
        self.session.headers = self.headers
        self.auth_method = self.login_prompt
        self.history = []

    def login_required(function):  # pylint: disable=E0213
        """ Decorator function that prompts user for login if they are not logged in already. Can be applied to any function using the @ notation. """
        def wrapper(self, *args, **kwargs):
            if 'Authorization' not in self.headers:
                self.auth_method()
            return function(self, *args, **kwargs)  # pylint: disable=E1102
        return wrapper

    def login(self, username=None, password=None, mfa_code=None, device_token=None):
        """Save and test login info for robinhood accounts

        Args:
            username (str): username
            password (str): password

        Returns:
            (bool): received valid auth token

        """
        if not username: username = input("Username: ")
        if not password: password = getpass.getpass()

        if not device_token:
            if self.current_device_token:
                device_token = self.current_device_token
            else:
                device_token = uuid.uuid1()
                self.current_device_token = device_token

        payload = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'device_token': device_token.hex,
            "token_type": "Bearer",
            'expires_in': 603995,
            "scope": "internal",
            'client_id': self.client_id,

        }

        if mfa_code:
            payload['access_token'] = self.auth_token
            payload['mfa_code'] = mfa_code
        else:
            payload['challenge_type'] = 'sms'

        try:
            res = self.session.post(endpoints.login(), data=payload, timeout=15, verify=True)
            res.raise_for_status()
            data = res.json()
            self.history.append(res)
        except requests.exceptions.HTTPError:
            raise RH_exception.LoginFailed()

        if 'mfa_required' in data.keys():
            mfa_code = input("MFA: ")
            return self.login(username, password, mfa_code, device_token)

        if 'access_token' in data.keys() and 'refresh_token' in data.keys():
            self.auth_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.headers['Authorization'] = 'Bearer ' + self.auth_token
            return res

        return False

    def logout(self):
        """Logout from robinhood

        Returns:
            (:obj:`requests.request`) result from logout endpoint

        """

        try:
            payload = {
                'client_id': self.client_id,
                'token': self.refresh_token
            }
            req = self.session.post(endpoints.logout(), data=payload, timeout=15)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log out ' + repr(err_msg))

        self.headers['Authorization'] = None
        self.auth_token = None

        return req

    ###########################################################################
    #                        SAVING AND LOADING SESSIONS
    ###########################################################################

    def save_session(self, session_name):
        with open(session_name + '.rb', 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load_session(session_name):
        with open(session_name + '.rb', 'rb') as file:
            return pickle.load(file)

    ###########################################################################
    #                               GET DATA
    ###########################################################################

    def investment_profile(self):
        """Fetch investment_profile """

        res = self.session.get(endpoints.investment_profile(), timeout=15)
        res.raise_for_status()  # will throw without auth
        data = res.json()

        return data


    def instrument(self, symbol):
        """Fetch instrument info

            Args:
                id (str): instrument id

            Returns:
                (:obj:`dict`): JSON dict of instrument
        """
        url = str(endpoints.instruments()) + "?symbol=" + str(symbol)

        try:
            req = requests.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidInstrumentId()

        return data['results']


    def get_quote(self, stock=''):
        """Fetch stock quote

            Args:
                stock (str): stock ticker, prompt if blank

            Returns:
                (:obj:`dict`): JSON contents from `quotes` endpoint
        """

        url = None

        stock = stock if isinstance(stock, list) else [stock]
        url = str(endpoints.quotes()) + "?symbols=" + ",".join(stock)

        # Check for validity of symbol
        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()

        return data


    def get_historical_quotes(self, stock, interval, span, bounds=Bounds.REGULAR):
        """Fetch historical data for stock

            Note: valid interval/span configs
                interval = 5minute | 10minute + span = day, week
                interval = day + span = year
                interval = week
                TODO: NEEDS TESTS

            Args:
                stock (str): stock ticker
                interval (str): resolution of data
                span (str): length of data
                bounds (:enum:`Bounds`, optional): 'extended' or 'regular' trading hours

            Returns:
                (:obj:`dict`) values returned from `historicals` endpoint
        """
        if type(stock) is str:
            stock = [stock]

        if isinstance(bounds, str):  # recast to Enum
            bounds = Bounds(bounds)

        historicals = endpoints.historicals() + "/?symbols=" + ','.join(stock).upper() + "&interval=" + interval + "&span=" + span + "&bounds=" + bounds.name.lower()

        res = self.session.get(historicals, timeout=15)
        return res.json()['results'][0]


    def get_account(self):
        """Fetch account information

            Returns:
                (:obj:`dict`): `accounts` endpoint payload
        """

        res = self.session.get(endpoints.accounts(), timeout=15)
        res.raise_for_status()  # auth required
        res = res.json()

        return res['results'][0]

    def get_url(self, url):
        """
            Flat wrapper for fetching URL directly
        """
        return self.session.get(url, timeout=15).json()

    @login_required
    def get_transfers(self):
        """Returns a page of list of transfers made to/from the Bank.

        Note that this is a paginated response. The consumer will have to look
        at 'next' key in the JSON and make a subsequent request for the next
        page.

            Returns:
                (list): List of all transfers to/from the bank.
        """
        res = self.session.get(endpoints.ach('transfers'), timeout=15)
        res.raise_for_status()
        return res.json()

    ###########################################################################
    #                           GET OPTIONS INFO
    ###########################################################################

    def get_options(self, stock, expiration_dates, option_type):
        """Get a list (chain) of options contracts belonging to a particular stock

            Args: stock ticker (str), list of expiration dates to filter on (YYYY-MM-DD), and whether or not its a 'put' or a 'call' option type (str).

            Returns:
                Options Contracts (List): a list (chain) of contracts for a given underlying equity instrument
        """
        instrument_id = self.get_url(self.quote_data(stock)["instrument"])["id"]
        if (type(expiration_dates) == list):
            _expiration_dates_string = ",".join(expiration_dates)
        else:
            _expiration_dates_string = expiration_dates
        chain_id = self.get_url(endpoints.chain(instrument_id))["results"][0]["id"]
        return [contract for contract in self.get_url(endpoints.options(chain_id, _expiration_dates_string, option_type))["results"]]

    @login_required
    def get_option_market_data(self, optionid):
        """Gets a list of market data for a given optionid.

        Args: (str) option id

        Returns: dictionary of options market data.
        """
        market_data = {}
        try:
            market_data = self.get_url(endpoints.market_data(optionid)) or {}
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidOptionId()
        return market_data


    ###########################################################################
    #                           GET FUNDAMENTALS
    ###########################################################################

    def fundamentals(self, stock=''):
        """Find stock fundamentals data

            Args:
                (str): stock ticker

            Returns:
                (:obj:`dict`): contents of `fundamentals` endpoint
        """

        #Prompt for stock if not entered
        if not stock:   # pragma: no cover
            stock = input("Symbol: ")

        url = str(endpoints.fundamentals(str(stock.upper())))

        #Check for validity of symbol
        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()
        return data


    ###########################################################################
    #                           PORTFOLIOS DATA
    ###########################################################################

    def portfolios(self):
        """Returns the user's portfolio data """

        req = self.session.get(endpoints.portfolios(), timeout=15)
        req.raise_for_status()

        return req.json()['results'][0]


    @login_required
    def order_history(self, orderId=None):
        """Wrapper for portfolios
            Optional Args: add an order ID to retrieve information about a single order.
            Returns:
                (:obj:`dict`): JSON dict from getting orders
        """
        return self.session.get(endpoints.orders(orderId), timeout=15).json()


    def dividends(self):
        """Wrapper for portfolios

            Returns:
                (:obj: `dict`): JSON dict from getting dividends
        """

        return self.session.get(endpoints.dividends(), timeout=15).json()


    ###########################################################################
    #                           POSITIONS DATA
    ###########################################################################

    def positions(self):
        """Returns the user's positions data

            Returns:
                (:object: `dict`): JSON dict from getting positions
        """

        return self.session.get(endpoints.positions(), timeout=15).json()


    def securities_owned(self):
        """Returns list of securities' symbols that the user has shares in

            Returns:
                (:object: `dict`): Non-zero positions
        """

        return self.session.get(endpoints.positions() + '?nonzero=true', timeout=15).json()


    ###########################################################################
    #                               PLACE ORDER
    ###########################################################################

    def place_market_buy_order(self,
                               symbol=None,
                               time_in_force=None,
                               quantity=None,
                               instrument_URL=None):
        """Wrapper for placing market buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self._submit_order(order_type='market',
                                  trigger='immediate',
                                  side='buy',
                                  instrument_URL=instrument_URL,
                                  symbol=symbol,
                                  time_in_force=time_in_force,
                                  quantity=quantity))

    def place_limit_buy_order(self,
                              instrument_URL=None,
                              symbol=None,
                              time_in_force=None,
                              price=None,
                              quantity=None):
        """Wrapper for placing limit buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                price (float): The max price you're willing to pay per share
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self._submit_order(order_type='limit',
                                  trigger='immediate',
                                  side='buy',
                                  instrument_URL=instrument_URL,
                                  symbol=symbol,
                                  time_in_force=time_in_force,
                                  price=price,
                                  quantity=quantity))

    def place_stop_loss_buy_order(self,
                                  instrument_URL=None,
                                  symbol=None,
                                  time_in_force=None,
                                  stop_price=None,
                                  quantity=None):
        """Wrapper for placing stop loss buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a market order
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self._submit_order(order_type='market',
                                  trigger='stop',
                                  side='buy',
                                  instrument_URL=instrument_URL,
                                  symbol=symbol,
                                  time_in_force=time_in_force,
                                  stop_price=stop_price,
                                  quantity=quantity))

    def place_stop_limit_buy_order(self,
                                   instrument_URL=None,
                                   symbol=None,
                                   time_in_force=None,
                                   stop_price=None,
                                   price=None,
                                   quantity=None):
        """Wrapper for placing stop limit buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a limit order
                price (float): The max price you're willing to pay per share
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self._submit_order(order_type='limit',
                                  trigger='stop',
                                  side='buy',
                                  instrument_URL=instrument_URL,
                                  symbol=symbol,
                                  time_in_force=time_in_force,
                                  stop_price=stop_price,
                                  price=price,
                                  quantity=quantity))

    def place_market_sell_order(self,
                                instrument_URL=None,
                                symbol=None,
                                time_in_force=None,
                                quantity=None):
        """Wrapper for placing market sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self._submit_order(order_type='market',
                                  trigger='immediate',
                                  side='sell',
                                  instrument_URL=instrument_URL,
                                  symbol=symbol,
                                  time_in_force=time_in_force,
                                  quantity=quantity))

    def place_limit_sell_order(self,
                               instrument_URL=None,
                               symbol=None,
                               time_in_force=None,
                               price=None,
                               quantity=None):
        """Wrapper for placing limit sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                price (float): The minimum price you're willing to get per share
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self._submit_order(order_type='limit',
                                  trigger='immediate',
                                  side='sell',
                                  instrument_URL=instrument_URL,
                                  symbol=symbol,
                                  time_in_force=time_in_force,
                                  price=price,
                                  quantity=quantity))

    def place_stop_loss_sell_order(self,
                                   instrument_URL=None,
                                   symbol=None,
                                   time_in_force=None,
                                   stop_price=None,
                                   quantity=None):
        """Wrapper for placing stop loss sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a market order
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self._submit_order(order_type='market',
                                  trigger='stop',
                                  side='sell',
                                  instrument_URL=instrument_URL,
                                  symbol=symbol,
                                  time_in_force=time_in_force,
                                  stop_price=stop_price,
                                  quantity=quantity))

    def place_stop_limit_sell_order(self,
                                    instrument_URL=None,
                                    symbol=None,
                                    time_in_force=None,
                                    price=None,
                                    stop_price=None,
                                    quantity=None):
        """Wrapper for placing stop limit sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a limit order
                price (float): The max price you're willing to get per share
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self._submit_order(order_type='limit',
                                  trigger='stop',
                                  side='sell',
                                  instrument_URL=instrument_URL,
                                  symbol=symbol,
                                  time_in_force=time_in_force,
                                  stop_price=stop_price,
                                  price=price,
                                  quantity=quantity))

    def _submit_order(self,
                      instrument_URL=None,
                      symbol=None,
                      order_type=None,
                      time_in_force=None,
                      trigger=None,
                      price=None,
                      stop_price=None,
                      quantity=None,
                      side=None):
        """Submits order to robinhood helper method of:
                place_market_buy_order()
                place_limit_buy_order()
                place_stop_loss_buy_order()
                place_stop_limit_buy_order()
                place_market_sell_order()
                place_limit_sell_order()
                place_stop_loss_sell_order()
                place_stop_limit_sell_order()

            Args:
                instrument_URL (str): the RH URL for the instrument
                symbol (str): the ticker symbol for the instrument
                order_type (str): 'MARKET' or 'LIMIT'
                time_in_force (:enum:`TIME_IN_FORCE`): GFD or GTC (day or
                                                       until cancelled)
                trigger (str): IMMEDIATE or STOP enum
                price (float): The share price you'll accept
                stop_price (float): The price at which the order becomes a
                                    market or limit order
                quantity (int): The number of shares to buy/sell
                side (str): BUY or sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        # Used for default price input
        # Price is required, so we use the current bid price if it is not specified
        current_quote = self.get_quote(symbol)
        current_bid_price = current_quote['bid_price']

        # Start with some parameter checks. I'm paranoid about $.
        if(instrument_URL is None):
            if(symbol is None):
                raise(ValueError('Neither instrument_URL nor symbol were passed to submit_order'))
            for result in self.instruments(symbol):
                if result['symbol'].upper() == symbol.upper():
                    instrument_URL = result['url']
                    break
            if(instrument_URL is None):
                raise(ValueError('instrument_URL could not be defined. Symbol %s not found' % symbol))

        if(symbol is None):
            symbol = self.session.get(instrument_URL, timeout=15).json()['symbol']

        if(side is None):
            raise(ValueError('Order is neither buy nor sell in call to submit_order'))

        if(order_type is None):
            if(price is None):
                if(stop_price is None):
                    order_type = 'market'
                else:
                    order_type = 'limit'

        symbol = str(symbol).upper()
        order_type = str(order_type).lower()
        time_in_force = str(time_in_force).lower()
        trigger = str(trigger).lower()
        side = str(side).lower()

        if(order_type != 'market') and (order_type != 'limit'):
            raise(ValueError('Invalid order_type in call to submit_order'))

        if(order_type == 'limit'):
            if(price is None):
                raise(ValueError('Limit order has no price in call to submit_order'))
            if(price <= 0):
                raise(ValueError('Price must be positive number in call to submit_order'))

        if(trigger == 'stop'):
            if(stop_price is None):
                raise(ValueError('Stop order has no stop_price in call to submit_order'))
            if(stop_price <= 0):
                raise(ValueError('Stop_price must be positive number in call to submit_order'))

        if(stop_price is not None):
            if(trigger != 'stop'):
                raise(ValueError('Stop price set for non-stop order in call to submit_order'))

        if(price is None):
            if(order_type == 'limit'):
                raise(ValueError('Limit order has no price in call to submit_order'))

        if(price is not None):
            if(order_type.lower() == 'market'):
                raise(ValueError('Market order has price limit in call to submit_order'))
            price = float(price)
        else:
            price = current_bid_price # default to current bid price

        if(quantity is None):
            raise(ValueError('No quantity specified in call to submit_order'))

        quantity = int(quantity)

        if(quantity <= 0):
            raise(ValueError('Quantity must be positive number in call to submit_order'))

        payload = {}

        for field, value in [
                ('account', self.get_account()['url']),
                ('instrument', instrument_URL),
                ('symbol', symbol),
                ('type', order_type),
                ('time_in_force', time_in_force),
                ('trigger', trigger),
                ('price', price),
                ('stop_price', stop_price),
                ('quantity', quantity),
                ('side', side)
            ]:
            if(value is not None):
                payload[field] = value

        print(payload)

        res = self.session.post(endpoints.orders(), data=payload, timeout=15)
        res.raise_for_status()

        return res

    ##############################
    #                          CANCEL ORDER
    ##############################

    def cancel_order(self, order_id):
        """
        Cancels specified order and returns the response (results from `orders` command).
        If order cannot be cancelled, `None` is returned.
        Args:
            order_id (str or dict): Order ID string that is to be cancelled or open order dict returned from
            order get.
        Returns:
            (:obj:`requests.request`): result from `orders` put command
        """
        if isinstance(order_id, str):
            try:
                order = self.session.get(endpoints.orders() + order_id, timeout=15).json()
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError('Failed to get Order for ID: ' + order_id + '\n Error message: ' + repr(err_msg))

            if order.get('cancel') is not None:
                try:
                    res = self.session.post(order['cancel'], timeout=15)
                    res.raise_for_status()
                    return res
                except (requests.exceptions.HTTPError) as err_msg:
                    raise ValueError('Failed to cancel order ID: ' + order_id + '\n Error message: '+ repr(err_msg))
                    return None

        if isinstance(order_id, dict):
            order_id = order_id['id']
            try:
                order = self.session.get(endpoints.orders() + order_id, timeout=15).json()
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError('Failed to get Order for ID: ' + order_id
                    + '\n Error message: '+ repr(err_msg))

            if order.get('cancel') is not None:
                try:
                    res = self.session.post(order['cancel'], timeout=15)
                    res.raise_for_status()
                    return res
                except (requests.exceptions.HTTPError) as err_msg:
                    raise ValueError('Failed to cancel order ID: ' + order_id
                         + '\n Error message: '+ repr(err_msg))
                    return None

        elif not isinstance(order_id, str) or not isinstance(order_id, dict):
            raise ValueError('Cancelling orders requires a valid order_id string or open order dictionary')


        # Order type cannot be cancelled without a valid cancel link
        else:
            raise ValueError('Unable to cancel order ID: ' + order_id)

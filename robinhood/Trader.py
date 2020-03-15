import warnings
from six.moves.urllib.request import getproxies
from six.moves import input

import getpass
import requests
import uuid
import pickle

from . import endpoints
from six.moves.urllib.parse import unquote


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

        res = self.session.post(endpoints.login(), data=payload, timeout=15, verify=True)
        res.raise_for_status()
        data = res.json()

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

    def is_logged_in(self):
        return "Authorization" in self.headers

    def _req_get(self, *args, timeout=15, **kwargs):
        res = self.session.get(*args, timeout=timeout, **kwargs)
        res.raise_for_status()
        return res

    def _req_get_json(self, *args, timeout=15, **kwargs):
        return self._req_get(*args, timeout=timeout, **kwargs).json()

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

    def fundamentals(self, symbol):
        return self._req_get_json(endpoints.fundamentals(symbol.upper()))

    def instrument(self, symbol):
        """Fetch instrument info

            Args:
                id (str): instrument id

            Returns:
                (:obj:`dict`): JSON dict of instrument
        """
        url = str(endpoints.instruments()) + "?symbol=" + str(symbol)
        return self._req_get_json(url)['results'][0]

    def quote(self, stock):
        """Fetch stock quote

            Args:
                stock (str): stock ticker

            Returns:
                (:obj:`dict`): JSON contents from `quotes` endpoint
        """
        stock = stock if isinstance(stock, list) else [stock]
        url = str(endpoints.quotes()) + "?symbols=" + ",".join(stock)
        return self._req_get(url).json()['results'][0]

    def historical_quotes(self, stock, interval, span, bounds='regular'):
        """Fetch historical data for stock

            Note: valid interval/span configs
                interval = 5minute | 10minute + span = day, week
                interval = day + span = year
                interval = week

            Args:
                stock (str): stock ticker
                interval (str): resolution of data
                span (str): length of data
                bounds (:enum:`Bounds`, optional): 'extended' or 'regular' trading hours

            Returns:
                (:obj:`dict`) values returned from `historicals` endpoint
        """
        stock = stock if isinstance(stock, list) else [stock]
        assert(bounds in ['immediate', 'regular'])

        url = endpoints.historicals()
        params = {
            'symbols': ','.join(stock).upper(),
            'interval': interval,
            'span': span,
            'bounds': bounds
        }
        url += '?' + '&'.join([f'{k}={v}' for k,v in params.items() if v])
        return self._req_get_json(url)['results'][0]

    ###########################################################################
    #                               Account Data
    ###########################################################################

    def account(self):
        res = self._req_get_json(endpoints.accounts())
        return res['results'][0]

    def portfolios(self):
        return self._req_get_json(endpoints.portfolios())['results'][0]

    def order_history(self):
        return self._req_get_json(endpoints.orders())

    def dividends(self):
        return self._req_get_json(endpoints.orders())

    ###########################################################################
    #                               PLACE ORDER
    ###########################################################################
    def place_buy_order(self,
                        symbol,
                        quantity,
                        price=None,
                        stop_price=None,
                        time_in_force=None):
        """
        Args:
            symbol: the stock symbol
            quantity: number of shares
            price: the limit price, if None defaults to a market order
            stop_price: the stop-loss price, if None defaults to an immediate (regular) order
            time_in_force: 'gfd' or 'gtc', gfd: cancel end of day, gtc: cancel until specified

        Returns:
            Response object
        """
        return self.place_order(symbol=symbol,
                                quantity=quantity,
                                price=price,
                                side='buy',
                                stop_price=stop_price,
                                time_in_force=time_in_force)

    def place_sell_order(
            self, symbol, quantity, price, stop_price=None, time_in_force=None):
        """
        Args:
            symbol: the stock symbol
            quantity: number of shares
            price: the limit price, if None defaults to a market order
            stop_price: the stop-loss price, if None defaults to an immediate (regular) order
            time_in_force: 'gfd' or 'gtc', gfd: cancel end of day, gtc: cancel until specified

        Returns:
            Response object
        """
        return self.place_order(symbol=symbol,
                                quantity=quantity,
                                price=price,
                                side='sell',
                                stop_price=stop_price,
                                time_in_force=time_in_force)

    def place_order(self,
                    symbol,
                    quantity,
                    side,
                    price=None,
                    stop_price=None,
                    time_in_force=None):
        """
        Args:
            symbol: the stock symbol
            quantity: number of shares
            price: the limit price, if None defaults to a market order
            stop_price: the stop-loss price, if None defaults to an immediate (regular) order
            time_in_force: 'gfd' or 'gtc', gfd: cancel end of day, gtc: cancel until specified

        Returns:
            Response object
        """

        return self._place_order_detail(
            self.instrument(symbol),
            quantity,
            price,
            stop_price,
            side,
            time_in_force)

    def _place_order_detail(
            self,
            instrument,
            quantity,
            price,
            stop_price,
            side,
            time_in_force=None):
        """Place an order with Robinhood
            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to
                    be traded
                quantity (int): quantity of stocks in order
                bid_price (float): price for order
                transaction (:enum:`Transaction`): BUY or SELL enum
                trigger: 'immediate' or 'stop'
                order: 'market' or 'limit'
                time_in_force 'gfd' or 'gtc'
            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        trigger = 'stop' if stop_price else 'immediate'
        order = 'limit' if price else 'market'
        time_in_force = time_in_force if time_in_force else 'gfd'
        assert(side in ['buy', 'sell'])
        if not price: price = self.quote(instrument["symbol"])["bid_price"]
        if not price: price = self.quote(instrument["symbol"])["last_trade_price"]
        if price is not None: price = float(price)
        if stop_price is not None: price = float(price)

        payload = {
            "account": self.account()["url"],
            "instrument": unquote(instrument["url"]),
            "symbol": instrument["symbol"],
            "type": order.lower(),
            "time_in_force": time_in_force,
            "trigger": trigger,
            "quantity": quantity,
            "side": side,
            'price': price,
            'stop_price': stop_price
        }

        res = self.session.post(endpoints.orders(), data=payload, timeout=15)
        res.raise_for_status()
        return res

    ###########################################################################
    #                               CANCEL ORDER
    ###########################################################################


    #TODO TEST
    def cancel_order(self, order_id):  # noqa: C901
        """
        Cancels specified order and returns the response (results from `orders`
            command).
        If order cannot be cancelled, `None` is returned.
        Args:
            order_id (str or dict): Order ID string that is to be cancelled or open
                order dict returned from
            order get.
        Returns:
            (:obj:`requests.request`): result from `orders` put command
        """
        if isinstance(order_id, str):
            try:
                order = self.session.get(
                    endpoints.orders() + order_id, timeout=15
                ).json()
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError(
                    "Failed to get Order for ID: "
                    + order_id
                    + "\n Error message: "
                    + repr(err_msg)
                )

            if order.get("cancel") is not None:
                try:
                    res = self.session.post(order["cancel"], timeout=15)
                    res.raise_for_status()
                    return res
                except requests.exceptions.HTTPError:
                    try:
                        # sometimes Robinhood asks for another log in when placing an
                        # order
                        res = self.session.post(
                            order["cancel"], headers=self.headers, timeout=15
                        )
                        res.raise_for_status()
                        return res
                    except (requests.exceptions.HTTPError) as err_msg:
                        raise ValueError(
                            "Failed to cancel order ID: "
                            + order_id
                            + "\n Error message: "
                            + repr(err_msg)
                        )
                        return None

        elif isinstance(order_id, dict):
            order_id = order_id["id"]
            try:
                order = self.session.get(
                    endpoints.orders() + order_id, timeout=15
                ).json()
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError(
                    "Failed to get Order for ID: "
                    + order_id
                    + "\n Error message: "
                    + repr(err_msg)
                )

            if order.get("cancel") is not None:
                try:
                    res = self.session.post(order["cancel"], timeout=15)
                    res.raise_for_status()
                    return res
                except requests.exceptions.HTTPError:
                    try:
                        # sometimes Robinhood asks for another log in when placing an
                        # order
                        res = self.session.post(
                            order["cancel"], headers=self.headers, timeout=15
                        )
                        res.raise_for_status()
                        return res
                    except (requests.exceptions.HTTPError) as err_msg:
                        raise ValueError(
                            "Failed to cancel order ID: "
                            + order_id
                            + "\n Error message: "
                            + repr(err_msg)
                        )
                        return None

        elif not isinstance(order_id, str) or not isinstance(order_id, dict):
            raise ValueError(
                "Cancelling orders requires a valid order_id string or open order"
                "dictionary"
            )

        # Order type cannot be cancelled without a valid cancel link
        else:
            raise ValueError("Unable to cancel order ID: " + order_id)

    def get_open_orders(self):
        """
        Returns all currently open (cancellable) orders.
        If not orders are currently open, `None` is returned.
        TODO: Is there a way to get these from the API endpoint without stepping through
            order history?
        """

        open_orders = []
        orders = self.order_history()
        for order in orders["results"]:
            if order["cancel"] is not None:
                open_orders.append(order)

        return open_orders

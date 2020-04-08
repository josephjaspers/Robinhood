# Robinhood_Trader

-------------------
This project was originally a fork of Jamonk's Unoffical Robinhood Api. 
However this project is considered to be a seperate project
as it contains significant changes. 

Changelist:  
 + Fixed/Added support for quoting crypto currencies
 + Fixed/Added support for buying/selling crypto currencies
 + Removed/Changed buy/sell interface 
 + Removed all quote-utility methods
 + Removed all usages of prompts (except for login)
 
------------------

### Getting Stared:
```python
from robinhood import Trader
trader = Trader('username', 'password') 
```
Logging in will prompt for an access_code which may be submitted  via a console prompt. 
```python
trader.save_session('filename')
```
Saves your current robinhood session for skipping logging in (until the cookie expires).  
 To restore your session:
```python
trader = Trader.load_session('filename')
```

### Trader methods 

#### Logging in and Sessions
```
 - login(username: str = None, password: str = None)
 - logout()
 - save_session(session_name: str)
 - load_session(session_name: str) @staticmethod 
```
#### Stock Data
```
 - fundamentals(symbol: str)
 - instrument(symbol: str)
 - quote (symbol: str)           # works for both crypto and regular stocks 
 - orderbook(symbol: str)        # requires robinhood gold
 - watch_orderbook(symbol: str)  # actively watch the orderbook in (pretty formatted)        
 - historical quotes(symbol: str)
```
#### Account Data 
```
 - account()
 - crypto_account()
 - orders()                         # returns order history 
 - crytpo_orders()                  # returns crypto order history 
 - order(order:Order)               # returns an updated order object from an existing Order 
 - crypto_order(order: CryptoOrder) # returns an updated crypto order object from an existing CryptoOrder object 
 - portfolios()
 - order_history()
 - dividends()
 ```
#### Trading 
```
 - buy(  
       symbol: str,                   # the stock symbol
       quantity: number,              # number of shares
       price: float = None,           # limit order if specified
       stop_price: float = None,      # stop order if specified
       trailing_stop_percent = None,  # trailing stop percent order (int) 5 -> trailing stop of 5%) 
       trailing_stop_amount = None,   # trailing stop price order 
       time_in_force = None,         # defaults to gfd (good for day)
       extended_hours = None)         # defaults to False if not suppplied 

 - sell(  
       symbol: str,                  # the stock symbol
       quantity: number,             # number of shares
       price: float = None,          # limit order if specified
       stop_price: float = None,     # stop order if specified
       trailing_stop_percent = None, # trailing stop percent order (int) 5 -> trailing stop of 5%) 
       trailing_stop_amount = None,  # trailing stop price order 
       time_in_force = None,         # defaults to gfd (good for day)
       extended_hours = None)        # defaults to False if not suppplied 

 - buy_crypto(  
       symbol: str,                   # the stock symbol
       quantity: number,              # number of shares
       price: float = None,           # limit order if specified
       time_in_force = None)          # defaults to gfd (good for day)

 - sell_crypto(  
       symbol: str,                   # the stock symbol
       quantity: number,              # number of shares
       price: float = None,           # limit order if specified
       time_in_force = None)          # defaults to gfd (good for day)
       
 - cancel(order: Order/CryptoOrder)   # cancels an existing order, returns response object, success does not ensure the order has been canceled). (Robinhood response does not indicate if the order was successfully canceled) 
 ```
 - For crypto-currencies, decimal quantities are supported. 

### The Quotes 

 - The quote object wraps a robinhood quote json and supplies convience functionality to it. 
 - to access the underlying json use `._dict`
 - Each property will on-the-fly convert to float, 
   this ensures that access to the original value is always available, (in case float conversion causes a loss of precision) 

#### Regular Quote 
##### Properties
 - ask -> float
 - bid -> float
 - last_trade_price -> float
 - previous_close -> float
 - adjusted_previous_close -> float
 - ask_size -> int
 - bid_size -> int

#### The CryptoQuote Object 
##### Properties
 - ask  -> float
 - bid  -> float
 - mark -> float   # market_price
 - high -> float
 - low  -> float
 - open -> float 

### The Orders 
 - The order objects wrap the order json and supply convienace definitions for basic functionality 
 - Properties are converted to their apropriate type on the fly, use `_dict`, to access the underlying json. 
 - Note, their are slight differences between crypto/regular orders. 

##### Methods 
 - update()               # updates the internal `_dict` by making a request to RH 
 - cancel()               # attempts to cancel the order, will fail on a filled/canceled order, success does not indicate cancelation. (Rh's response does not indicate the status of the order). 
 - filled(update: bool = True) -> bool # returns if the order has been filled, if update is true, will call update prior.
 - canceled(update: bool = True) -> bool # returns if the order has been canceled, if update is true, will call update prior.
 - status(update: bool = True) -> str    # returns the current status of the order. ( 

##### Properties 
 - time -> pd.Timestamp   # returns timestamp when we received the response from robinhood (not RH's timestamp!)
 - price -> float         # price  
 - side  -> str           # 'buy' or 'sell'
 - quantity -> (int if regular order, float if crypto_order) # needs update once fractional shares are supported 




---------------------
#### Original fork: https://github.com/robinhood-unofficial/Robinhood

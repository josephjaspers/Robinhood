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
 + Removed all usages of prompts (accept for login)
 
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
Saves your current robinhood session so you do not need to login again (until the cookie expires). To restore your session:
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
 - quote (symbol: str)
 - historical quotes(symbol: str)
```
#### Account Data 
```
 + account()
 + portfolios() 
 + order_history()
 + dividends()
 ```
####Trading 
```
 - buy(  
       symbol: str,               # the stock symbol
       quantity: number,          # number of shares
       price: float = None,       # limit order if specified
       stop_price: float = None)  # stop order if specified

 - sell(  
       symbol: str,               # the stock symbol
       quantity: number,          # number of shares
       price: float = None,       # limit order if specified
       stop_price: float = None)  # stop order if specified

 ```
 - For crypto-currencies, decimal quantities are supported. 


---------------------
#### Original fork: https://github.com/robinhood-unofficial/Robinhood
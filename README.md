# Robinhood

-------------------

This is a fork of the original repository. 
Credits to Jamonek for writing the original version
This version contains SIGNIFICANT changes to the original version


Changelist: 

1) Removed a large number of features that were either poorly tested, not useful, or duplicates of existing functionality
2) Refactored a large amount of the code for better use,
3) Removed all prompting related methods (except for login)
4) Removed default 'None' parameters that would cause an exception if not supplied 
       IE (methods like 'buy_market_order' would have quantity marked as optional)   

------------------

[![Join the chat at https://gitter.im/J-Robinhood/Lobby](https://badges.gitter.im/J-Robinhood/Lobby.svg)](https://gitter.im/J-Robinhood/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
Python Framework to make trades with Robinhood Private API.
See this [blog post](https://medium.com/@rohanpai25/reversing-robinhood-free-accessible-automated-stock-trading-f40fba1e7d8b).

## Current Features 
- Placing buy orders (`Robinhood.place_buy_order`)
- Placing sell order (`Robinhood.place_sell_order`)
- Fetch and cancel orders (`Robinhood.order_history` and `Robinhood.cancel_order`)
- Quote information (`Robinhood.quote_data`)
- User portfolio data (`Robinhood.portfolios`)
- User positions data (`Robinhood.positions`)
- More coming soon

### How To Install:
Clone the repository into your project directory using:

    git clone https://github.com/Jamonek/Robinhood

Then navigate to the cloned directory, where `setup.py` is located. Now run the following to install:

    pip install .

### How to Use (see [example.py](https://github.com/Jamonek/Robinhood/blob/master/docs/example.py))

    from Robinhood import Robinhood
    my_trader = Robinhood()
    logged_in = my_trader.login(username="USERNAME HERE", password="PASSWORD HERE")
    stock_instrument = my_trader.instrument("GEVO")
    buy_order = my_trader.place_market_buy_order('AAPL', 1)

### Data returned
* Quote data
  + Ask Price
  + Ask Size
  + Bid Price
  + Bid Size
  + Last trade price
  + Previous close
  + Previous close date
  + Adjusted previous close
  + Trading halted
  + Updated at
  + Historical Price
* User portfolio data
  + Adjusted equity previous close
  + Equity
  + Equity previous close
  + Excess margin
  + Extended hours equity
  + Extended hours market value
  + Last core equity
  + Last core market value
  + Market value
  + Order history
  + Dividend history
* User positions data
  + Securities owned
* News

------------------

# Related

* [robinhood-ruby](https://github.com/rememberlenny/robinhood-ruby) - RubyGem for interacting with Robinhood API
* [robinhood-node](https://github.com/aurbano/robinhood-node) - NodeJS module to make trades with Robinhood Private API

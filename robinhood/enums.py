from enum import Enum

class Bounds(Enum):
    """Enum for bounds in `historicals` endpoint """

    REGULAR = 'regular'
    EXTENDED = 'extended'


class Transaction(Enum):
    """Enum for buy/sell orders """

    BUY = 'buy'
    SELL = 'sell'


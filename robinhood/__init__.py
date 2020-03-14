import six

if six.PY3:
    from .Trader import Trader
else:
    from .Trader import Trader

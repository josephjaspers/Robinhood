import six

if six.PY3:
    from .trader import Trader
else:
    from .trader import Trader

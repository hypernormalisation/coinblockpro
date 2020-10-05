import itertools
import random

_asset_list = [
    'btc',
    'ltc',
    'eth',
    'etc',
    'xlm',
    'xrp',
    'bch',
    'dot',
    'eur',
    'usd',
]
_pairs = itertools.combinations(_asset_list, 2)
markets = ['_'.join(t) for t in _pairs]
ticker_data_conditions = {}
for market in markets:
    ticker_data_conditions[market] = round(random.uniform(0, 10000), 3)

# Ticker database properties
db_path = '/tmp/tickers.db'
url = f'sqlite:///{db_path}'
table_name = 'tickers'
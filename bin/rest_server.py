#!/usr/bin/env python3
"""Script to run a Sanic REST server, to be used in conjunction
with the ws_server.py script.

Together, these scripts provide a toy simulation of an exchange's
last price tickers.
"""
import dataset
import time
import coinblockpro

from sanic import Sanic
from sanic.log import logger
from sanic.response import json


ticker_data = {
    'a': 1200.1,
    'b': 400.34,
    'c': 500.31,
}


###########################################################
# Functions to manipulate the ticker and db.
###########################################################
def load_full_ticker():
    """Load all tickers from the sqlite db."""
    with dataset.connect(coinblockpro.url) as db:
        t = db[coinblockpro.table_name]
        result = list(t.all())
    return {d['market']: d['price'] for d in result}


def load_single_ticker(market):
    """Load the ticker for the given market from the sqlite db."""
    with dataset.connect(coinblockpro.url) as db:
        t = db[coinblockpro.table_name]
        result = t.find_one(market=market)
    return {result['market']: result['price']}


###########################################################
# The Sanic app.
###########################################################
app = Sanic("exchange")


@app.route("/full_ticker")
async def get_full_ticker(request):
    """Get the full ticker, i.e. for all markets."""
    logger.info('Received a full ticker request.')
    return json({'result': load_full_ticker()})


@app.route('/single_ticker')
async def get_single_ticker(request):
    """Get a single market ticker. The market parameter must be given."""
    logger.info('Received a single ticker request.')
    request_args = request.get_args()
    if 'market' not in request_args:
        return json(
            {'error': 'must give "market" parameter!'},
            status=400,
        )
    logger.debug(request_args)
    market = request_args['market'][0]
    if market not in ticker_data:
        return json(
            {'error': 'market code not recognised!'},
            status=400,
        )
    return json({'result': load_single_ticker(market)})


if __name__ == "__main__":
    time.sleep(1)  # give time for the ws server to run
    logger.info('Running REST server.')
    app.run(host="0.0.0.0", port=8000)

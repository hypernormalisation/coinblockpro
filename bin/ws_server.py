#!/usr/bin/env python3
"""Script to run a Sanic websocket server, simulating
and serving the last prices of a series of markets
that fluctuate over time.

Market data is persisted to an SQL db, so that a separate
process running a REST server can serve http requests.
"""
import asyncio
import pathlib
import random

import dataset

import coinblockpro

from sanic import Sanic
from sanic.log import logger
from sanic.websocket import WebSocketProtocol

from coinblockpro import ticker_data_conditions

###########################################################
# Initial configuration
###########################################################
random.seed(512320390)

# Placeholder for a global asyncio event, to notify the
# websocket server when the market price changes.
# Will be set once the event loop starts.
ticker_event = None
MARKET_BUFFER = None


###########################################################
# Functions to manipulate the ticker and db.
###########################################################
def write_initial_ticker_to_db():
    """Write the initial ticker conditions to the database, first
    deleting any existing database.
    """
    db_file = pathlib.Path(coinblockpro.db_path)
    db_file.unlink(missing_ok=True)

    with dataset.connect(coinblockpro.url) as db:
        t = db[coinblockpro.table_name]
        for market, price in ticker_data_conditions.items():
            t.insert(dict(market=market, price=price))


def update_market(market, price):
    """Update the in-memory vars and SQL db for the specified market.
    Also push the market to the buffer.
    """
    global MARKET_BUFFER
    ticker_data_conditions[market] = price
    with dataset.connect(coinblockpro.url) as db:
        t = db[coinblockpro.table_name]
        t.update(dict(market=market, price=price), keys=['market'])
    MARKET_BUFFER = {market: price}


def get_market_from_buffer():
    """Get the market from the buffer and clear the buffer."""
    global MARKET_BUFFER
    payload = str(MARKET_BUFFER)
    MARKET_BUFFER = None
    return payload


# noinspection PyUnresolvedReferences
async def modulate_ticker_data():
    """Coroutine to modulate a random ticker, by a random
    amount, at a random interval. Also write the new ticker
    value to the ticker database.
    """
    try:
        logger.info('Starting modulation coroutine.')
        while True:
            interval = random.gauss(5, 2)
            await asyncio.sleep(interval)

            market = random.choice(list(ticker_data_conditions.keys()))
            price_original = ticker_data_conditions[market]
            price_new = round(
                random.gauss(price_original, price_original * 0.02),
                3
            )
            logger.info(f'update to market {market}: '
                        f'{price_original} -> {price_new}')
            update_market(market, price_new)
            ticker_event.set()
    except KeyboardInterrupt:
        pass

###########################################################
# Configure the Sanic instance.
###########################################################
app = Sanic("exchange_websocket")
app.add_task(modulate_ticker_data)


@app.listener('before_server_start')
def init_event(sanic, loop):
    """Assign the global event once the loop has started."""
    global ticker_event
    ticker_event = asyncio.Event()


# noinspection PyUnresolvedReferences
@app.websocket('/ticker_feed')
async def feed(request, ws):
    """Websocket feed for live ticker updates."""
    while True:
        await ticker_event.wait()
        logger.info('Broadcasting market change to websockets.')
        payload = get_market_from_buffer()
        await ws.send(payload)
        ticker_event.clear()

if __name__ == "__main__":
    # Create the ticker db.
    logger.info(f'Creating ticker db at {coinblockpro.db_path}.')
    write_initial_ticker_to_db()
    logger.info('Created db.')

    # Run websocket server.
    logger.info('Running websocket server.')
    app.run(host="0.0.0.0", port=8001, protocol=WebSocketProtocol)

import asyncio
import pathlib
import random

import dataset

from sanic import Sanic
from sanic.log import logger
from sanic.websocket import WebSocketProtocol


# Placeholder for a global asyncio event, to notify the
# websocket server when the market price updates.
# Will be set once the event loop starts.
ticker_event = None

# Create the database objects.
db_path = '/tmp/tickers.db'
url = f'sqlite:///{db_path}'
table_name = 'tickers'
MARKET_BUFFER = None


# Seed the random number generator and create the ticker.
random.seed(512320390)
ticker_data_conditions = {
    'btc_eur': 1200.125,
    'btc_usd': 1300.421,
    'eth_btc': 400.34,
    'ltc_btc': 123.12,
    'ltc_eth': 500.31,
}


def write_initial_ticker_to_db():
    """Write the initial ticker conditions to the database, first
    deleting any existing database.
    """
    db_file = pathlib.Path(db_path)
    db_file.unlink(missing_ok=True)

    with dataset.connect(url) as db:
        t = db[table_name]
        for market, price in ticker_data_conditions.items():
            t.insert(dict(market=market, price=price))


def update_market(market, price):
    """Update the in-memory vars and SQL db for the specified market.
    Also push the market to the buffer.
    """
    global MARKET_BUFFER
    ticker_data_conditions[market] = price
    with dataset.connect(url) as db:
        t = db[table_name]
        t.update(dict(market=market, price=price), keys=['market'])
    MARKET_BUFFER = {market: price}


app = Sanic("exchange_websocket")


@app.listener('before_server_start')
def init_event(sanic, loop):
    """Assign the global event once the loop has started."""
    global ticker_event
    ticker_event = asyncio.Event()


# noinspection PyUnresolvedReferences
@app.websocket('/ticker_feed')
async def feed(request, ws):
    while True:
        await ticker_event.wait()
        logger.info('Broadcasting market change to websockets.')
        payload = get_market_from_buffer()
        await ws.send(payload)
        # logger.info('Broadcast complete, clearing event.')
        ticker_event.clear()


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

app.add_task(modulate_ticker_data)

if __name__ == "__main__":

    # Create the ticker db.
    logger.info(f'Creating ticker db at {db_path}.')
    write_initial_ticker_to_db()
    logger.info('Created db.')

    # Run websocket server.
    logger.info('Running websocket server.')
    app.run(host="0.0.0.0", port=8001, protocol=WebSocketProtocol)

# coinblockpro

A toy server written in Sanic to mimic an online currency exchange, with
REST and websocket APIs.

## Installation

`coinblockpro` is available on the Python Package Index (PyPI).

`pip install coinblockpro`

## Run

The bash script `run_cbp_server` is placed in the user's bin when the
package is installed. Running:

`./run_cbp_server`

will produce output like the following:

```
[2020-10-05 19:19:37 +0100] [34227] [INFO] Creating ticker db at /tmp/tickers.db.
[2020-10-05 19:19:37 +0100] [34227] [INFO] Created db.
[2020-10-05 19:19:37 +0100] [34227] [INFO] Running websocket server.
[2020-10-05 19:19:37 +0100] [34227] [INFO] Goin' Fast @ http://0.0.0.0:8001
[2020-10-05 19:19:37 +0100] [34227] [INFO] Starting modulation coroutine.
[2020-10-05 19:19:37 +0100] [34227] [INFO] Starting worker [34227]
[2020-10-05 19:19:38 +0100] [34228] [INFO] Running REST server.
[2020-10-05 19:19:38 +0100] [34228] [INFO] Goin' Fast @ http://0.0.0.0:8000
[2020-10-05 19:19:38 +0100] [34228] [INFO] Starting worker [34228]
[2020-10-05 19:19:43 +0100] [34227] [INFO] update to market btc_ltc: 3350.505 -> 3292.16
[2020-10-05 19:19:49 +0100] [34227] [INFO] update to market ltc_dot: 2752.763 -> 2708.661
```

## Connecting to the server

The server runs on the localhost.

The REST API is available on port 8000, while the websocket API is
available on port 8001.

### REST endpoints:

`/full_ticker` - no parameters, returns a json response of the form:

```
{ 'result':  
    {'btc_eur':  2134.12, 'btc_usd': 2245.76} ... }
}
```

`/single_ticker` - single parameter "market", must be given. Returns a
json response of the form:

```
{ 'result':
    {'btc_eur': 2134.12}
}
```

The list of available markets can be found at:

```python
import coinblockpro
coinblockpro.markets
```

Some example requests are given below:

```python
import requests
r1 = requests.get('http://0.0.0.0:8000/full_ticker')
r2 = requests.get('http://0.0.0.0:8000/singler_ticker', params={'market': 'btc_eur'})
```

### Websocket API

The websocket API runs on the localhost, on port 8001, and gives
real-time information on markets as they change at the `/ticker_feed`
endpoint.

An example configuration using the `websockets` library is given below.

```python
import websockets
import asyncio
import websockets


async def subscribe():
    async with websockets.connect('ws://0.0.0.0:8001/ticker_feed') as ws:
        while True:
            resp = await ws.recv()
            print(resp)

if __name__ == '__main__':
    asyncio.run(subscribe())

```

## Example client

UNDER CONSTRUCTION
import asyncio
import websockets


async def subscribe():
    async with websockets.connect('ws://0.0.0.0:8001/ticker_feed') as ws:
        while True:
            resp = await ws.recv()
            print(resp)

if __name__ == '__main__':
    asyncio.run(subscribe())

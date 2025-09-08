import asyncio
from websockets.asyncio.server import serve


async def fn(websocket):
    print(websocket,'websocket')
    async for meg in websocket:
        print(websocket,'msg',meg)
        await websocket.send(f'msg fromserver {meg} ')


async def main():
    print('xxxxxxxxxxxxxxx')
    async with serve (fn,'localhost',8001) as server:
        await server.serve_forever()

asyncio.run(main())

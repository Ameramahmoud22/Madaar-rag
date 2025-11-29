# test_ws.py
import asyncio
import json
import websockets


async def main():
    uri = "ws://127.0.0.1:8000/ws/chat/?token=8c7561b3c2b1233fbd16a74d3f8a4fac00cf2d6a"
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"query": "hello"}))
            while True:
                msg = await ws.recv()
                print("recv:", msg)
    except Exception as e:
        print("error:", e)
asyncio.run(main())

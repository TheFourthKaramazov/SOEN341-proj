import asyncio
import websockets
import json


async def fake_user():
    async with websockets.connect("ws://localhost:8000/realtime/direct/2") as websocket:
        print("✅ Fake User 2 connected!")

        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📩 Message received: {data}")


asyncio.run(fake_user())

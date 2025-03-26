import asyncio
import websockets
from client_manager import register, unregister
from pubsub_listener import start_listener


async def handler(websocket, path):
    print("Client connected")
    await register(websocket)
    try:
        async for message in websocket:
            print(f"Received from client: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        unregister(websocket)


async def main():
    start_listener("receipt-tracking-application", "webapp-sub")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

connected_clients = set()


async def register(websocket):
    connected_clients.add(websocket)


def unregister(websocket):
    connected_clients.remove(websocket)


async def broadcast(data):
    if connected_clients:
        await asyncio.gather(*(client.send(data) for client in connected_clients))

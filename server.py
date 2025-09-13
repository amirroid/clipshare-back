import asyncio
import websockets
import os
import json

connections = {}

async def handler(websocket):
    headers = websocket.request.headers if hasattr(websocket, "request") else {}
    device_id = headers.get("uid")

    if device_id:
        connections[device_id] = websocket
    print(f"Device connected: {device_id}")

    try:
        async for message in websocket:
            print(f"Received from {device_id}: {message}")
            try:
                msg = json.loads(message)
                target_ws = connections.get(msg.get("to"))
                if target_ws and target_ws.open:
                    await target_ws.send(message)
            except Exception as e:
                print("Error parsing message:", e)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if device_id in connections:
            del connections[device_id]
        print(f"Device disconnected: {device_id}")

async def main():
    port = int(os.environ.get("PORT", 8080))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"WebSocket server running on ws://0.0.0.0:{port}")
        await asyncio.Future()  # keep running

if __name__ == "__main__":
    asyncio.run(main())

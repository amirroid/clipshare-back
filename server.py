import os
import json
from aiohttp import web

connections = {}

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    device_id = request.headers.get("uid")
    if device_id:
        connections[device_id] = ws
        print(f"Device connected: {device_id}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                target = connections.get(data.get("to"))
                if target is not None:
                    await target.send_json(data)
    finally:
        if device_id in connections:
            del connections[device_id]
            print(f"Device disconnected: {device_id}")

    return ws

async def health(request):
    return web.Response(text="OK")

def main():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/signaling", ws_handler)

    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

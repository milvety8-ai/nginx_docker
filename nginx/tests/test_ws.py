# tests/test_ws.py
import asyncio
import json

import websockets

async def test_websocket():
    uri = "ws://ws.localhost/ws"
    async with websockets.connect(uri) as ws:
        # Получить welcome-сообщение от сервера.
        welcome = await ws.recv()
        welcome_data = json.loads(welcome)
        print(f"Welcome: {welcome_data}")
        assert welcome_data["type"] == "welcome"

        # ws-server эхо-ответом возвращает исходную строку, а не JSON.
        message = "Hello, NGINX!"
        await ws.send(message)

        # Проверяем, что через nginx проксируется обычное echo-сообщение.
        echo = await ws.recv()
        if isinstance(echo, bytes):
            echo = echo.decode()
        print(f"Echo received: {echo}")
        assert echo == message
        print("✅ WebSocket proxy works correctly!")

asyncio.run(test_websocket())

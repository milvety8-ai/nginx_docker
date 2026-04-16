# tests/test_ws.py
import asyncio, json, websockets

async def test_websocket():
    uri = "ws://ws.localhost/ws"
    async with websockets.connect(uri) as ws:
        # Получить welcome сообщение
        welcome = await ws.recv()
        print(f"Welcome: {json.loads(welcome)}") 

        # Отправить сообщение
        await ws.send('Hello, NGINX!')

        # Получить echo
        echo = await ws.recv()
        data = json.loads(echo)
        print(f"Echo received: {data['original']} at {data['timestamp']}")
        assert data['type'] == 'echo'
        print('✅ WebSocket proxy works correctly!')

asyncio.run(test_websocket())
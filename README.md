# nginx + docker-compose (gateway)

Запуск:

```bash
docker compose up --build
```

После старта:

- `http://localhost/` — статическая страница
- `http://localhost/api/v1/` — API v1
- `http://localhost/api/v2/` — API v2
- `http://localhost/api/slow/` — медленный API (по умолчанию ~3 сек)
- `ws://localhost/ws` — WebSocket (echo)

HTTPS:

- `https://localhost/` — работает на самоподписанном сертификате из `nginx/ssl/` (браузер будет ругаться — это нормально для локалки)

Порты можно переопределить:

```bash
HTTP_PORT=8080 HTTPS_PORT=8443 docker compose up --build
```

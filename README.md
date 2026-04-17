# Отчет по лабораторной работе

## Тема
NGINX + Docker Compose: конфигурирование веб-сервера и локальной микросервисной инфраструктуры.

## Цель работы
Собрать локальный стенд с NGINX в роли reverse proxy и gateway, настроить маршрутизацию к нескольким backend-сервисам, HTTPS, rate limiting, proxy cache, WebSocket proxy, JSON-логирование и базовый мониторинг.

## Использованный стек
- NGINX `1.25-alpine`
- Docker Compose
- Python Flask для `api_v1`, `api_v2`, `api_slow`
- Node.js + `ws` для WebSocket-сервера
- OpenSSL для самоподписанных сертификатов
- `curl` и Python-скрипты для проверки
- Prometheus + NGINX Exporter как бонусная часть

## Структура проекта
```text
.
├── docker-compose.yml
├── README.md
├── prometheus.yml
├── nginx
│   ├── nginx.conf
│   ├── conf.d
│   │   ├── default.conf
│   │   ├── proxy.conf
│   │   ├── security.conf
│   │   ├── ssl.conf
│   │   └── ws.conf
│   ├── html
│   │   ├── index.html
│   │   ├── 404.html
│   │   └── 50x.html
│   ├── ssl
│   │   ├── .htpasswd
│   │   ├── cert.pem
│   │   ├── key.pem
│   │   ├── server.crt
│   │   └── server.key
│   └── tests
│       ├── test_all.sh
│       └── test_ws.py
└── services
    ├── api-slow
    │   ├── app.py
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── api-v1
    │   ├── app.py
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── api-v2
    │   ├── app.py
    │   ├── Dockerfile
    │   └── requirements.txt
    └── ws-server
        ├── Dockerfile
        ├── package.json
        └── server.js
```

## Состав сервисов
- `nginx_gateway` — центральный gateway, reverse proxy, HTTPS termination, cache, rate limit.
- `api_v1` — backend API версии `v1`.
- `api_v2` — backend API версии `v2`.
- `api_slow` — медленный backend для тестирования upstream и отказоустойчивости.
- `ws_server` — WebSocket echo-сервер.
- `nginx_exporter` — экспорт метрик NGINX для Prometheus.
- `prometheus` — сбор и просмотр метрик.

## Запуск проекта
```bash
docker compose up --build -d
docker compose ps
```

## Актуальный статус контейнеров
```text
NAME                            IMAGE                                    STATUS
api_slow                        nginx_docker-api_slow                    Up
api_v2                          nginx_docker-api_v2                      Up
nginx_docker-nginx_exporter-1   nginx/nginx-prometheus-exporter:latest   Up
nginx_docker-prometheus-1       prom/prometheus                          Up
nginx_gateway                   nginx:1.25-alpine                        Up
ws_server                       nginx_docker-ws_server                   Up
```

## Что реализовано

### 1. Базовая конфигурация NGINX и статика
- Настроен основной `nginx.conf` с `worker_processes auto`, `gzip`, `server_tokens off`.
- Подключено JSON-логирование в расширенном формате.
- Настроена раздача статического сайта из `nginx/html`.
- Добавлены кастомные страницы ошибок `404.html` и `50x.html`.
- Доступен `stub_status` на `/nginx_status`.

Проверки:
```bash
curl -I http://localhost/
curl -I https://localhost/ -k
curl -I https://localhost/nonexistent -k
curl http://localhost/nginx_status
```

### 2. Location, redirect и rewrite
- Реализован редирект `/old-api -> /api`.
- Добавлен `location = /favicon.ico` с кодом `204`.
- Закрыт доступ к скрытым файлам вида `/.env`.
- Добавлен пример rewrite для `/blog/<id>`.
- В ответы добавляется `X-Request-ID`.

### 3. Reverse proxy и маршрутизация к backend
- Выделен виртуальный хост `api.localhost`.
- Настроено проксирование к `api_v1` и `api_v2`.
- Передаются заголовки `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.
- Добавлена карта `map $uri $api_version`.

Проверки:
```bash
curl http://api.localhost/api/v1/info
curl http://api.localhost/api/v2/info
```

### 4. Балансировка нагрузки
- Настроены upstream-блоки с разными стратегиями:
- `api_pool` — weighted round-robin.
- `api_fair` — `least_conn`.
- `api_sticky` — `ip_hash`.
- Для балансировщика добавлены диагностические заголовки upstream.

### 5. HTTPS
- Настроен HTTPS на `443` с самоподписанными сертификатами.
- Реализован редирект с HTTP на HTTPS для `localhost`.
- Для HTTPS-маршрутов сохранено проксирование API.

Проверки:
```bash
curl -I http://localhost/
curl -k https://localhost/
```

### 6. Безопасность
- Настроен `secure.localhost`.
- Добавлены security headers:
- `X-Frame-Options`
- `X-Content-Type-Options`
- `X-XSS-Protection`
- `Referrer-Policy`
- `Permissions-Policy`
- `Content-Security-Policy`
- Реализован `rate limiting`.
- Добавлен `basic auth` для приватного маршрута.
- Ограничен доступ к `/admin`.

Проверка rate limit:
```bash
for i in {1..40}; do
  curl -s -o /dev/null -w '%{http_code}\n' http://secure.localhost/api/v1/info
done
```

### 7. Proxy cache
- В `http` добавлен `proxy_cache_path`.
- Подключен volume `nginx_cache:/var/cache/nginx`.
- Настроен кэширующий маршрут `/api/cached/`.
- В ответ выводится статус кэша в заголовке `X-Cache`.

Проверки:
```bash
curl -I http://api.localhost/api/cached/info
curl -I http://api.localhost/api/cached/info
```

Типичный сценарий:
- Первый запрос: `MISS`
- Повторный запрос: `HIT`

### 8. WebSocket proxy
- Настроен отдельный виртуальный хост `ws.localhost`.
- Проксируется маршрут `/ws`.
- Передаются заголовки `Upgrade` и `Connection`.
- Проверен echo-обмен сообщениями через NGINX.

Проверка:
```bash
python3 nginx/tests/test_ws.py
```

### 9. Логирование и анализ
- Используется JSON-формат `json_extended`.
- В логах присутствуют:
- `time`
- `ip`
- `method`
- `uri`
- `args`
- `status`
- `bytes`
- `duration`
- `upstream`
- `upstream_time`
- `cache`
- `ua`
- `referer`

Примеры анализа:
```bash
docker exec nginx_gateway tail -10 /var/log/nginx/access.log | python3 -m json.tool
docker exec nginx_gateway sh -c "tail -50 /var/log/nginx/access.log"
```

### Бонусная часть
- Подключен `nginx-prometheus-exporter`.
- Подключен `prometheus`.
- Метрики доступны на `http://localhost:9090` и `http://localhost:9113/metrics`.

## Основные проблемы и как они были исправлены

### Ошибка запуска NGINX
Изначально `nginx_gateway` уходил в restart loop. Причина:
- `log_format` был объявлен вне блока `http`.
- `access_log` также находился в недопустимом контексте.

Решение:
- `log_format json_extended` перенесен внутрь `http`.
- `access_log` оставлен только в валидном месте внутри `http`.

### Проблема WebSocket-теста
Изначальный `test_ws.py` ожидал JSON-объект в echo-ответе, но текущий `ws_server` возвращал исходную строку.

Решение:
- тест приведен к реальному поведению сервера.
- добавена обработка случая, когда библиотека возвращает echo как `bytes`.

## Результаты тестирования

### Автоматическая проверка HTTP/HTTPS/API/cache/rate-limit
```text
✅ Static HTML serves
✅ NGINX hides version
✅ Gzip enabled
✅ 404 custom page
✅ API v1 proxy works
✅ API v2 proxy works
✅ HTTPS redirect
✅ HTTPS works
✅ Rate limit returns 429
✅ Cache HIT on 2nd request

Results: 10 passed, 0 failed
```

### Проверка WebSocket
```text
Welcome: {'type': 'welcome', 'remote': '172.20.0.6'}
Echo received: Hello, NGINX!
✅ WebSocket proxy works correctly!
```

## Ответы на ключевые вопросы из задания

### Зачем нужен `proxy_cache_lock on`
`proxy_cache_lock on` предотвращает ситуацию, когда много одновременных запросов к одному и тому же еще не закэшированному ресурсу одновременно уходят в upstream. При включенном lock первый запрос идет к backend, а остальные ждут его результат. Без него backend получает всплеск одинаковых запросов, что увеличивает нагрузку и время ответа.

### Почему для WebSocket нужны `Upgrade` и `Connection`
WebSocket начинается как HTTP-запрос, а затем переключается на постоянное двустороннее соединение. Заголовок `Upgrade: websocket` сообщает о желании сменить протокол, а `Connection: Upgrade` разрешает это переключение на уровне HTTP. Если не передать эти заголовки через proxy, handshake не завершится, и соединение останется обычным HTTP-запросом или завершится ошибкой.

## Выводы
- На практике закреплена настройка NGINX как reverse proxy, HTTPS termination и точки входа для нескольких сервисов.
- Отработаны стратегии балансировки, rate limiting, базовые security headers и проксирование WebSocket.
- Дополнительно настроен экспорт метрик в Prometheus и проверена работоспособность.


# Events Aggregator

## Описание

Сервис агрегирует события из внешнего Events Provider API, предоставляет API для получения событий и регистрации на них, а также реализует:

* Transactional Outbox для надежной доставки уведомлений
* Идемпотентность регистрации билетов
* Интеграцию с сервисом уведомлений Capashino
* Мониторинг ошибок через GlitchTip (Sentry SDK)

---

## Запуск

### Локально

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Переменные окружения

```env
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=5432
POSTGRES_DATABASE_NAME=

X_API_KEY=
EXTERNAL_API_URL=

CAPASHINO_API_URL=
CAPASHINO_API_KEY=

SENTRY_DSN=

OUTBOX_WORKER_INTERVAL=5
OUTBOX_BATCH_SIZE=10
```

---

## API

### Получение событий

```
GET /api/events/
```

Параметры:

* `page`
* `page_size`
* `date_from`

---

### Получение события

```
GET /api/events/{event_id}/
```

---

### Получение доступных мест

```
GET /api/events/{event_id}/seats/
```

---

## Регистрация на событие

```
POST /api/tickets
```

### Тело запроса

```json
{
  "event_id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "seat": "string",
  "idempotency_key": "string (optional)"
}
```

---

### Ответ

```json
{
  "ticket_id": "uuid"
}
```

---

## Идемпотентность

Если передан `idempotency_key`:

* Повторный запрос с теми же данными → вернёт тот же `ticket_id`
* Повторный запрос с другим телом → `409 Conflict`

Если ключ не передан — каждый запрос создаёт новый билет.

---

## Удаление билета

```
DELETE /api/tickets/{ticket_id}
```

---

## Transactional Outbox

При создании билета:

1. Билет сохраняется в БД
2. Создается запись в outbox
3. Коммит происходит атомарно

Фоновый воркер:

* читает pending события
* отправляет уведомление в Capashino
* при успехе помечает как `sent`
* при ошибке оставляет событие для повторной обработки

---

## Capashino

После успешной регистрации:

* отправляется уведомление через API Capashino
* используется `idempotency_key` для защиты от дублей
* при ошибке отправка повторяется через Outbox

---

## GlitchTip

Используется `sentry-sdk`.

* DSN берётся из переменной окружения `SENTRY_DSN`
* все необработанные ошибки автоматически отправляются
* используется интеграция FastAPI

---

## Метрики

```
GET /metrics
```

Prometheus метрики через `prometheus-fastapi-instrumentator`

---

## Линтер

```bash
ruff check .
```

---

## Архитектура

* FastAPI
* PostgreSQL
* SQLAlchemy (async)
* Alembic
* Outbox pattern
* Background workers

---

## Особенности

* защита от дублей (идемпотентность)
* устойчивость к падению внешних сервисов
* ретраи через outbox
* масштабируемая архитектура

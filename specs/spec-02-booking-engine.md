# SPEC-02: Booking Engine

> Техническая спецификация модуля бронирования платформы Т-Командировка
> Версия: 1.0 | 1 марта 2026 | Статус: Draft

---

## 1. Обзор модуля

### 1.1 Назначение

Booking Engine -- центральный модуль платформы Т-Командировка, обеспечивающий единый интерфейс бронирования всех типов услуг корпоративного travel-менеджмента:

| Тип услуги | Провайдеры | SLA поиска |
|------------|-----------|------------|
| Авиабилеты | Amadeus, Sirena, Sabre, прямые API авиакомпаний | < 5 сек |
| Ж/д билеты | РЖД (Sirena), Аэроэкспресс | < 3 сек |
| Отели | Ostrovok API, прямые контракты, 3D-контракты | < 4 сек |
| Такси | Яндекс Go API | < 2 сек |
| Трансферы | Собственная база, партнёрские API | < 3 сек |

### 1.2 Место в архитектуре

Booking Engine располагается между уровнем представления (веб-интерфейс, мобильное приложение, AI-агент, Telegram-бот) и внешними провайдерами. Модуль принимает нормализованные запросы от API Gateway и возвращает структурированные ответы.

```
+-------------------------------------------------------------------+
|                       КЛИЕНТСКИЙ УРОВЕНЬ                          |
|  +----------+  +----------+  +----------+  +------------------+  |
|  | Web App  |  | Mobile   |  | Telegram |  | AI Agent (NLU)   |  |
|  +----+-----+  +----+-----+  +----+-----+  +--------+---------+  |
|       +______________+______________+________________+            |
+---------------------------+---------------------------------------+
                            | REST / gRPC
                    +-------v-------+
                    |  API Gateway  |
                    |  (Kong/Envoy) |
                    +-------+-------+
                            |
  +-------------------------v--------------------------------------+
  |                    BOOKING ENGINE                               |
  |                                                                |
  |  +----------------+  +----------------+  +-----------------+   |
  |  | Search         |  | Booking        |  | Policy          |   |
  |  | Aggregator     |  | Service        |  | Engine          |   |
  |  +-------+--------+  +-------+--------+  +--------+--------+   |
  |          |                   |                     |            |
  |  +-------v--------+  +------v---------+  +-------v--------+   |
  |  | Pricing        |  | Inventory      |  | Provider       |   |
  |  | Engine         |  | Cache          |  | Adapters       |   |
  |  +----------------+  +----------------+  +----------------+   |
  +----------------------------------------------------------------+
                            |
              +-------------+-------------+
              |             |             |
        +-----v-----+ +----v----+ +------v------+
        | PostgreSQL | |  Redis  | | Kafka       |
        +-----------+ +---------+ +-------------+
```

### 1.3 Принципы проектирования

1. **Provider-agnostic** -- бизнес-логика не зависит от конкретного поставщика.
2. **Fail-fast, degrade gracefully** -- при отказе провайдера результаты возвращаются от остальных.
3. **Idempotent operations** -- все мутирующие операции идемпотентны.
4. **Event-driven** -- изменения состояния публикуются в Kafka.
5. **Policy-first** -- каждое бронирование проходит проверку тревел-политики.

---

## 2. Архитектура

### 2.1 Микросервисы

| Сервис | Стек | Ответственность |
|--------|------|-----------------|
| `search-aggregator` | Go, gRPC | Параллельный поиск, merge, dedup, ranking |
| `booking-service` | Kotlin / Spring Boot | State machine бронирования, оркестрация |
| `pricing-engine` | Go | Fare rules, корпоративные тарифы, markup, валюты |
| `inventory-cache` | Go + Redis | Кэширование результатов и цен |
| `policy-engine` | Kotlin / Spring Boot | Механизм правил тревел-политики |
| `provider-adapter-*` | Go | Отдельный адаптер на каждого провайдера |
| `notification-worker` | Python | Обработка событий Kafka, рассылка уведомлений |

### 2.2 Межсервисное взаимодействие

Синхронные вызовы (gRPC): search-aggregator -> provider-adapter-*, booking-service -> pricing-engine.
Асинхронные события (Kafka): все изменения состояния публикуются в топик `booking.events`.

| Топик | Producers | Consumers |
|-------|-----------|-----------|
| `booking.events` | booking-service | notification-worker, analytics, accounting |
| `search.requests` | search-aggregator | provider-adapter-* |
| `search.results` | provider-adapter-* | search-aggregator |
| `policy.evaluations` | policy-engine | booking-service, analytics |
| `price.updates` | pricing-engine | inventory-cache |

### 2.3 Поток данных при поиске

```
Пользователь       API Gateway      Search Aggregator     Provider Adapters
    |                    |                  |                     |
    |  POST /flights/    |                  |                     |
    |  search            |                  |                     |
    |====================>  forward         |                     |
    |                    |=================>|                     |
    |                    |                  |  fan-out (parallel)  |
    |                    |                  |====================>| Amadeus
    |                    |                  |====================>| Sirena
    |                    |                  |====================>| Sabre
    |                    |                  |====================>| S7 Direct
    |                    |                  |                     |
    |                    |                  |  <== results =======| (async)
    |                    |                  |  merge + dedup      |
    |                    |                  |  rank + policy check|
    |                    |  <== response ===|                     |
    |  <== 200 OK =======|                  |                     |
```

---

## 3. Поиск авиабилетов

### 3.1 Интеграция с провайдерами (Adapter Pattern)

Каждый провайдер реализует единый интерфейс:

```go
type FlightProvider interface {
    Search(ctx context.Context, req *SearchRequest) (*SearchResponse, error)
    GetFareRules(ctx context.Context, offerId string) (*FareRules, error)
    Hold(ctx context.Context, offerId string, passengers []Passenger) (*HoldResult, error)
    Book(ctx context.Context, holdId string, payment PaymentInfo) (*BookResult, error)
    Cancel(ctx context.Context, bookingRef string) (*CancelResult, error)
    GetBookingStatus(ctx context.Context, bookingRef string) (*BookingStatus, error)
}
```

#### Карта провайдеров

| Провайдер | Протокол | Timeout | Rate Limit | Покрытие |
|-----------|----------|---------|------------|----------|
| Amadeus | REST API v2 | 8 сек | 40 TPS | Международные рейсы |
| Sirena/Travelport | XML/SOAP | 10 сек | 20 TPS | СНГ, внутренние рейсы |
| Sabre | REST/SOAP | 8 сек | 30 TPS | Международные рейсы |
| S7 Airlines | REST API | 5 сек | 15 TPS | Прямые тарифы S7 |
| Аэрофлот | NDC API | 6 сек | 10 TPS | Прямые тарифы |
| Победа | REST API | 4 сек | 10 TPS | Лоукост-тарифы |
| Уральские авиалинии | REST API | 5 сек | 10 TPS | Прямые тарифы |

#### Стратегия кэширования провайдеров

| Тип данных | TTL | Storage | Invalidation |
|-----------|-----|---------|--------------|
| Результаты поиска | 15 мин | Redis | По TTL + ручная |
| Pricing / Fare | 30 мин | Redis | По TTL |
| Расписание рейсов | 24 часа | Redis | По событию |
| Маршрутная сеть | 7 дней | PostgreSQL + Redis | По расписанию |

### 3.2 Search API

#### POST /api/v1/flights/search

**Request:**

```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440000",
  "trip_type": "round_trip",
  "segments": [
    {
      "origin": "SVO",
      "destination": "KZN",
      "departure_date": "2026-03-10",
      "time_preference": { "from": "06:00", "to": "14:00" }
    },
    {
      "origin": "KZN",
      "destination": "SVO",
      "departure_date": "2026-03-12",
      "time_preference": null
    }
  ],
  "passengers": [
    {
      "type": "adult",
      "first_name": "Ivan",
      "last_name": "Petrov",
      "loyalty_programs": ["S7 Priority"]
    }
  ],
  "cabin_class": "economy",
  "flexible_dates": true,
  "flex_range_days": 3,
  "direct_only": false,
  "max_stops": 1,
  "preferred_airlines": ["S7", "SU"],
  "corporate_id": "tbank-corp-001",
  "policy_id": "policy-default-v2",
  "currency": "RUB"
}
```

**Response:**

```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "search_time_ms": 3420,
  "providers_queried": ["amadeus", "sirena", "s7_direct"],
  "providers_failed": [],
  "total_results": 47,
  "results": [
    {
      "offer_id": "offer-abc-123",
      "provider": "sirena",
      "itinerary": {
        "segments": [
          {
            "segment_id": "seg-1",
            "flight_number": "S7 1144",
            "airline": { "code": "S7", "name": "S7 Airlines" },
            "aircraft": { "code": "32A", "name": "Airbus A320" },
            "origin": {
              "airport": "SVO", "terminal": "B", "city": "Москва",
              "departure_time": "2026-03-10T08:30:00+03:00"
            },
            "destination": {
              "airport": "KZN", "terminal": "1", "city": "Казань",
              "arrival_time": "2026-03-10T10:15:00+03:00"
            },
            "duration_minutes": 105,
            "stops": 0,
            "baggage": { "included_kg": 23, "carry_on_kg": 10 },
            "cabin_class": "economy",
            "fare_class": "Y",
            "seats_available": 14
          }
        ],
        "total_duration_minutes": 105
      },
      "pricing": {
        "total": 8450.00,
        "currency": "RUB",
        "breakdown": {
          "base_fare": 6200.00,
          "taxes": 1850.00,
          "fees": 200.00,
          "service_fee": 200.00
        },
        "price_per_passenger": 8450.00,
        "corporate_discount": null,
        "price_valid_until": "2026-03-01T15:30:00+03:00"
      },
      "fare_rules": {
        "refundable": true,
        "changeable": true,
        "change_fee": 2500.00,
        "cancel_fee": 3000.00,
        "no_show_fee": 6200.00
      },
      "policy_compliance": {
        "status": "COMPLIANT",
        "violations": [],
        "warnings": []
      }
    }
  ],
  "filters": {
    "airlines": [
      { "code": "S7", "name": "S7 Airlines", "count": 12, "min_price": 7800 },
      { "code": "SU", "name": "Аэрофлот", "count": 18, "min_price": 9200 },
      { "code": "DP", "name": "Победа", "count": 8, "min_price": 4500 }
    ],
    "stops": [
      { "value": 0, "label": "Прямые", "count": 32, "min_price": 4500 },
      { "value": 1, "label": "1 пересадка", "count": 15, "min_price": 6200 }
    ],
    "price_range": { "min": 4500, "max": 28400, "currency": "RUB" }
  },
  "flexible_dates_matrix": {
    "2026-03-08": 7200, "2026-03-09": 6800,
    "2026-03-10": 8450, "2026-03-11": 7900,
    "2026-03-12": 9100, "2026-03-13": 7400
  }
}
```

#### Алгоритм ранжирования

```
score = w1*price_norm + w2*duration_norm + w3*stops_penalty
      + w4*policy_bonus + w5*preferred_airline + w6*time_match
```

| Фактор | Вес | Описание |
|--------|-----|----------|
| `price_norm` | 0.35 | Нормализованная цена (min-max) |
| `duration_norm` | 0.20 | Нормализованная длительность |
| `stops_penalty` | 0.15 | Штраф за пересадки |
| `policy_bonus` | 0.15 | Бонус за соответствие политике |
| `preferred_airline` | 0.10 | Бонус за предпочтительную а/к |
| `time_preference` | 0.05 | Соответствие желаемому времени |

### 3.3 Pricing и Fare Rules

#### Классы тарифов

| Класс | Коды | Возврат | Обмен | Багаж | UI |
|-------|------|---------|-------|-------|----|
| Промо | L, K | Нет | Нет | Нет | Невозвратный |
| Эконом | Y, B, H | Частичный | Платный | 1x23 кг | Стандарт |
| Эконом Плюс | M, Q | Да | Да | 1x23 кг | Гибкий |
| Бизнес | C, D, J | Да | Да | 2x32 кг | Бизнес |

#### Корпоративные тарифы

```json
{
  "corporate_rate_id": "cr-tbank-s7-2026",
  "airline": "S7",
  "discount_type": "percentage",
  "discount_value": 12.0,
  "cabin_classes": ["economy", "business"],
  "routes": ["SVO-KZN", "SVO-LED", "SVO-SVX"],
  "valid_from": "2026-01-01",
  "valid_to": "2026-12-31",
  "min_advance_days": 3
}
```

#### Валютные расчёты

Все расчёты в RUB. Международные рейсы пересчитываются по курсу ЦБ РФ + 0.5% markup (обновление каждые 30 мин).

```
Итоговая цена = base_fare + taxes + platform_fee + markup - corporate_discount
```

---

## 4. Поиск ж/д билетов

### 4.1 Интеграция с РЖД

Интеграция через Sirena-Travel API (XML/SOAP), fallback на прямой API АО ФПК.

| Параметр | Значение |
|----------|----------|
| Протокол | XML/SOAP через Sirena-Travel |
| Timeout | 8 сек |
| Rate Limit | 20 TPS |
| Кэш расписания | 6 часов |
| Кэш цен | 15 мин |

### 4.2 Типы вагонов и мест

| Тип | Код | Описание | Уровень цены |
|-----|-----|----------|--------------|
| Сидячий | С | Сидячие места | $ |
| Плацкарт | П | Открытые полки | $$ |
| Купе | К | 4-местное купе | $$$ |
| СВ | Л | 2-местное купе | $$$$ |
| Люкс | М | 1-местное купе | $$$$$ |

Выбор места:

```json
{
  "seat_preference": {
    "berth": "lower",
    "position": "window",
    "near_socket": true
  }
}
```

### 4.3 POST /api/v1/trains/search

```json
{
  "origin_station": "2000000",
  "destination_station": "2004001",
  "departure_date": "2026-03-10",
  "departure_time_from": "06:00",
  "departure_time_to": "23:00",
  "passengers": [{ "type": "adult", "document_type": "passport_rf" }],
  "car_type": ["coupe", "sv"],
  "seat_preference": { "berth": "lower" },
  "include_aeroexpress": true,
  "corporate_id": "tbank-corp-001"
}
```

### 4.4 Электронная регистрация

Для маршрутов с поддержкой ЭР билет оформляется без посещения кассы. Система автоматически определяет доступность и оформляет e-ticket. Аэроэкспресс интегрирован для маршрутов SVO, DME, VKO.

---

## 5. Поиск отелей

### 5.1 Провайдеры

| Провайдер | Тип | Покрытие | Timeout |
|-----------|-----|----------|---------|
| Ostrovok API | Агрегатор | 2.5M+ объектов | 6 сек |
| Прямые контракты | Bilateral | Cosmos, Azimut, Marriott RU | 4 сек |
| 3D-контракты | Корпоративные | Договорные ставки | 3 сек |

### 5.2 POST /api/v1/hotels/search

**Request:**

```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440001",
  "location": { "type": "city", "city_code": "KZN" },
  "check_in": "2026-03-10",
  "check_out": "2026-03-12",
  "rooms": [{ "adults": 1, "children": [], "room_type_preference": "standard" }],
  "filters": {
    "star_rating_min": 3,
    "star_rating_max": 5,
    "price_max": 8000,
    "meal_plan": ["breakfast"],
    "amenities": ["wifi", "parking"],
    "free_cancellation": true,
    "distance_to": {
      "type": "address",
      "address": "ул. Баумана, 36, Казань",
      "max_km": 5
    }
  },
  "sort_by": "price_asc",
  "corporate_id": "tbank-corp-001",
  "policy_id": "policy-default-v2",
  "currency": "RUB",
  "page": 1,
  "page_size": 20
}
```

**Response:**

```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "completed",
  "total_results": 124,
  "results": [
    {
      "offer_id": "hotel-offer-456",
      "provider": "ostrovok",
      "hotel": {
        "hotel_id": "htl-kzn-001",
        "name": "Kazan Palace by Tasigo",
        "star_rating": 5,
        "address": "ул. Баумана, 6/8, Казань",
        "location": { "lat": 55.7887, "lng": 49.1221 },
        "distance_km": 0.3,
        "photos": [
          { "url": "https://cdn.t-komandirovka.ru/hotels/kzn-001/main.jpg", "type": "main" }
        ],
        "amenities": ["wifi", "parking", "gym", "restaurant", "spa"],
        "rating": { "score": 8.9, "reviews_count": 1247 },
        "check_in_time": "14:00",
        "check_out_time": "12:00"
      },
      "room": {
        "room_type": "standard_double",
        "room_name": "Стандарт с двуспальной кроватью",
        "meal_plan": "breakfast",
        "bed_type": "double",
        "max_occupancy": 2,
        "area_sqm": 28
      },
      "pricing": {
        "total": 12400.00,
        "per_night": 6200.00,
        "currency": "RUB",
        "breakdown": { "room_rate": 11200.00, "taxes": 1000.00, "service_fee": 200.00 },
        "corporate_rate_applied": false
      },
      "cancellation": {
        "free_cancellation_until": "2026-03-08T23:59:00+03:00",
        "penalty_after": { "amount": 6200.00, "type": "first_night" }
      },
      "policy_compliance": { "status": "COMPLIANT" }
    }
  ]
}
```

### 5.3 Корпоративные vs публичные тарифы

Система проверяет наличие корпоративного тарифа в `corporate_hotel_rates`. Если доступен -- отображается приоритетно с пометкой. Публичные тарифы показываются параллельно.

### 5.4 Фотографии и CDN

Фото кэшируются на CDN (S3-compatible). Ресайз: thumbnail 200x150, medium 600x400, large 1200x800. TTL -- 30 дней.

---

## 6. Транспорт на месте

### 6.1 Такси (Яндекс Go API)

#### POST /api/v1/taxi/order

**Request:**

```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440002",
  "corporate_id": "tbank-corp-001",
  "employee_id": "emp-12345",
  "pickup": { "address": "аэропорт Казань, терминал 1", "lat": 55.6062, "lng": 49.2787 },
  "dropoff": { "address": "ул. Баумана, 6/8, Казань", "lat": 55.7887, "lng": 49.1221 },
  "tariff": "business",
  "scheduled_time": "2026-03-10T10:30:00+03:00",
  "payment": { "type": "corporate", "cost_center": "CC-SALES-001" },
  "ride_limit_rub": 3000
}
```

**Response:**

```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "accepted",
  "driver": { "name": "Алексей", "car": "Toyota Camry", "plate": "А123БВ116", "eta_minutes": 12 },
  "estimated_price": { "amount": 1450.00, "currency": "RUB" },
  "ride_limit_check": "WITHIN_LIMIT",
  "tracking_url": "https://taxi.t-komandirovka.ru/track/550e8400"
}
```

#### Лимиты поездок

| Уровень | Описание | При превышении |
|---------|----------|----------------|
| Per-ride | Макс. стоимость одной поездки | Блокировка |
| Daily | Макс. сумма в день | Предупреждение / блокировка |
| Monthly | Макс. сумма в месяц | Блокировка до нового месяца |

### 6.2 Трансферы

#### POST /api/v1/transfers/search

**Request:**

```json
{
  "pickup": { "type": "airport", "code": "KZN", "terminal": "1" },
  "dropoff": { "type": "hotel", "address": "ул. Баумана, 6/8, Казань" },
  "datetime": "2026-03-10T10:30:00+03:00",
  "passengers": 1, "luggage": 1, "vehicle_class": "business"
}
```

**Response:**

```json
{
  "options": [
    {
      "offer_id": "transfer-001",
      "vehicle_class": "business",
      "vehicle": "Mercedes E-class или аналог",
      "max_passengers": 3,
      "price": { "amount": 2800.00, "currency": "RUB" },
      "duration_minutes": 35,
      "cancellation": { "free_until_hours": 24, "penalty": 1400.00 },
      "driver_meets_with_sign": true
    }
  ]
}
```

### 6.3 Аренда автомобилей (future)

Зарезервирован: `POST /api/v1/car-rental/search`. Детали в SPEC-02a.

---

<!-- SECTION_BREAK_2 -->

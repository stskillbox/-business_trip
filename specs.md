# Технические спецификации: Т-Командировка

> Technical Specifications v1.0
> Дата: 1 марта 2026
> Статус: Draft
> Связанные документы: [PRD](./prd.md) · [UX/UI](./ux-ui-design.md) · [Анализ](./T-Komandirovka-Analysis.md)

---

## Содержание

1. [SPEC-1: AI-Агент](#spec-1-ai-агент)
2. [SPEC-2: Бронирование](#spec-2-бронирование)
3. [SPEC-3: Управление командировками](#spec-3-управление-командировками)
4. [SPEC-4: Финансовый модуль](#spec-4-финансовый-модуль)
5. [SPEC-5: Аналитика и BI](#spec-5-аналитика-и-bi)
6. [SPEC-6: MICE](#spec-6-mice)
7. [SPEC-7: Интеграции](#spec-7-интеграции)
8. [SPEC-8: Инфраструктура](#spec-8-инфраструктура)

---

# SPEC-1: AI-АГЕНТ

## 1.1. Обзор

AI-агент «Т-Помощник» — центральная точка входа в продукт. Пользователь общается с ботом на естественном языке, а агент парсит intent, собирает параметры через уточняющие вопросы и выполняет действия: поиск билетов/отелей, создание заявок, загрузка чеков, формирование отчётов, аналитика расходов.

### Каналы доступа

| Канал | Поддержка | Фаза |
|-------|-----------|------|
| Web-чат (встроен в платформу) | Полная | MVP |
| Мобильное приложение (iOS/Android) | Полная | MVP |
| Telegram-бот | Текст + inline-кнопки + фото | MVP |
| Голосовой ввод (Speech-to-Text) | Микрофон → текст → стандартный pipeline | v1.1 |

### Архитектура AI-агента

```
┌─────────────────────────────────────────────────────────────────┐
│                        КЛИЕНТ (Web / Mobile / Telegram)         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Chat UI                                                  │   │
│  │  • Input field + attachments                              │   │
│  │  • Message stream (SSE / WebSocket)                       │   │
│  │  • Inline components (cards, buttons, summaries)          │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                            │
├─────────────────────┼────────────────────────────────────────────┤
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Gateway / BFF                                        │   │
│  │  POST /api/v1/chat/message                                │   │
│  │  GET  /api/v1/chat/history                                │   │
│  │  POST /api/v1/chat/feedback                               │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  AGENT ORCHESTRATOR                                       │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │ Intent      │  │ Slot        │  │ Dialog          │  │   │
│  │  │ Classifier  │→ │ Extractor   │→ │ Manager         │  │   │
│  │  │             │  │             │  │ (state machine) │  │   │
│  │  └─────────────┘  └─────────────┘  └────────┬────────┘  │   │
│  │                                              │            │   │
│  │  ┌───────────────────────────────────────────┘            │   │
│  │  ▼                                                        │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │ Action      │  │ Response    │  │ Context         │  │   │
│  │  │ Executor    │→ │ Generator   │→ │ Store           │  │   │
│  │  │ (tools)     │  │ (LLM)       │  │ (Redis/PG)      │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  BACKEND SERVICES (через internal API)                    │   │
│  │  • BookingService    • ApprovalService                    │   │
│  │  • ExpenseService    • AnalyticsService                   │   │
│  │  • DocumentService   • PolicyService                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1.2. Intents (намерения)

### Реестр интентов

| ID | Intent | Описание | Пример фразы | Приоритет |
|----|--------|----------|--------------|-----------|
| `book.flight` | Поиск/бронирование авиабилета | «Найди билет в Казань на 10 марта» | P0 |
| `book.train` | Поиск/бронирование ж/д | «Сапсан до Питера в пятницу» | P0 |
| `book.hotel` | Поиск/бронирование отеля | «Отель в Казани до 5000₽ за ночь» | P0 |
| `book.taxi` | Заказ такси/трансфера | «Такси из Шереметьево в офис» | P0 |
| `book.complex` | Комплексная командировка | «Мне нужно в Казань вт-чт, билет + отель» | P0 |
| `trip.create` | Создание заявки на командировку | «Оформи командировку Иванову в Екатеринбург» | P0 |
| `trip.status` | Статус заявки/поездки | «Где мой билет?» «Что с заявкой?» | P0 |
| `trip.cancel` | Отмена/изменение бронирования | «Отмени билет в Казань» | P0 |
| `expense.report` | Авансовый отчёт | «Оформи авансовый отчёт за Казань» | P0 |
| `expense.receipt` | Загрузка чека (OCR) | [фото чека] «Добавь этот чек» | P1 |
| `expense.status` | Статус авансового отчёта | «На какой стадии мой отчёт?» | P1 |
| `analytics.spend` | Аналитика расходов | «Сколько потратили в феврале?» | P1 |
| `analytics.budget` | Бюджет и лимиты | «Какой бюджет остался на квартал?» | P1 |
| `policy.check` | Проверка тревел-политики | «Можно ли бизнес-класс в Сочи?» | P1 |
| `mice.create` | Создание мероприятия | «Организуй конференцию на 50 человек в Сочи» | P1 |
| `personal.trip` | Личная поездка | «Хочу в отпуск, найди отель в Турции» | P1 |
| `approval.list` | Список на согласование (для руководителя) | «Что ждёт моего одобрения?» | P0 |
| `approval.action` | Согласовать/отклонить | «Одобри заявку Петрова» | P0 |
| `help` | Помощь / возможности | «Что ты умеешь?» | P0 |
| `greeting` | Приветствие | «Привет» | P0 |
| `fallback` | Не распознан | Любой нераспознанный текст | P0 |

### Классификация интентов

**Модель**: Fine-tuned модель на базе ruGPT / YandexGPT / собственная LLM.

**Fallback-стратегия**: Если confidence < 0.65 → уточняющий вопрос. Если < 0.3 → предложение выбрать из вариантов.

```
Входное сообщение
       │
       ▼
┌──────────────┐     confidence >= 0.65
│ Intent       │────────────────────────→ Slot Extraction
│ Classifier   │
└──────┬───────┘
       │ confidence 0.3-0.65
       ▼
┌──────────────┐
│ Clarify:     │  «Вы хотите найти билет или
│ "Уточните..."│   создать заявку на командировку?»
└──────────────┘
       │ confidence < 0.3
       ▼
┌──────────────┐
│ Fallback:    │  «Не совсем понял. Вот что я умею:
│ Show options │   [Найти билет] [Заявка] [Отчёт]»
└──────────────┘
```

---

## 1.3. Slots (параметры)

### Реестр слотов по интентам

#### `book.flight` / `book.complex`

| Slot | Тип | Обязательный | Пример | Prompt при отсутствии |
|------|-----|-------------|--------|----------------------|
| `origin` | City | Да (default: город сотрудника) | «Москва», «SVO» | «Из какого города вылетаете?» |
| `destination` | City | Да | «Казань», «KZN» | «Куда летим?» |
| `date_departure` | Date | Да | «10 марта», «вторник», «послезавтра» | «Когда вылет?» |
| `date_return` | Date | Нет | «13 марта» | «Нужен обратный билет? Если да — на какую дату?» |
| `passengers` | Integer | Нет (default: 1) | «2 человека» | — |
| `class` | Enum | Нет (default: economy) | «бизнес-класс» | — |
| `baggage` | Boolean | Нет | «с багажом» | «Нужен ли багаж?» → [23 кг] [Только ручная кладь] |
| `employee` | Employee | Нет (default: текущий) | «для Иванова» | — |
| `trip_id` | TripID | Нет | «к командировке #1247» | — |

#### `book.hotel`

| Slot | Тип | Обязательный | Пример | Prompt при отсутствии |
|------|-----|-------------|--------|----------------------|
| `city` | City | Да | «Казань» | «В каком городе нужен отель?» |
| `checkin` | Date | Да | «10 марта» | «Дата заезда?» |
| `checkout` | Date | Да | «13 марта» | «Дата выезда?» |
| `max_price` | Money | Нет | «до 5000₽» | — |
| `breakfast` | Boolean | Нет | «с завтраком» | «Нужен ли завтрак?» → [С завтраком] [Без завтрака] |
| `stars_min` | Integer | Нет | «от 4 звёзд» | — |
| `employee` | Employee | Нет (default: текущий) | «для Петровой» | — |

#### `expense.receipt`

| Slot | Тип | Обязательный | Пример | Prompt при отсутствии |
|------|-----|-------------|--------|----------------------|
| `image` | File (JPEG/PNG) | Да | [прикреплённое фото] | «Прикрепите фото чека» |
| `trip_id` | TripID | Нет | «за Казань» | «К какой командировке отнести?» (список последних) |
| `category` | Enum | Нет (auto via OCR) | «такси» | — |

### Парсинг дат

| Формат ввода | Интерпретация |
|-------------|---------------|
| «10 марта» | 2026-03-10 |
| «вторник» | Ближайший вторник (если прошёл — следующий) |
| «послезавтра» | today + 2 |
| «через неделю» | today + 7 |
| «со вторника по четверг» | departure: вторник, return: четверг |
| «на 2 ночи» | checkout = checkin + 2 |
| «10-13 марта» | departure: 10, return: 13 |
| «в начале апреля» | Уточняющий вопрос: «Конкретные даты?» |

### Парсинг городов

Fuzzy matching с базой городов РФ (1100+) и международных (50 000+).

| Ввод | Город | IATA |
|------|-------|------|
| «Питер» | Санкт-Петербург | LED |
| «Мск» | Москва | MOW |
| «Ебург», «Екб» | Екатеринбург | SVX |
| «Казань» | Казань | KZN |
| «Новосиб» | Новосибирск | OVB |
| «Нижний» | Нижний Новгород | GOJ |

---

## 1.4. Dialog Manager (управление диалогом)

### State Machine для `book.complex`

```
                    ┌──────────────┐
                    │   START      │
                    └──────┬───────┘
                           │ user message
                           ▼
                    ┌──────────────┐
                    │ PARSE_INTENT │
                    │ + EXTRACT    │
                    │   SLOTS      │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
      all required    missing       ambiguous
      slots filled    slots         intent
              │            │            │
              │            ▼            ▼
              │    ┌──────────────┐  ┌──────────────┐
              │    │ ASK_SLOT     │  │ CLARIFY      │
              │    │ (sequential) │  │ INTENT       │
              │    └──────┬───────┘  └──────┬───────┘
              │           │                 │
              │           │ slot filled     │ intent confirmed
              │           ▼                 │
              │    ┌──────────────┐         │
              │    │ MORE_SLOTS?  │─────────┘
              │    └──────┬───────┘
              │           │ all filled
              ▼           ▼
       ┌──────────────────────────┐
       │   ASK_OPTIONAL_SLOTS    │
       │   (return? → baggage?   │
       │    → hotel? → transfer?)│
       └──────────┬───────────────┘
                  │ all answered / skipped
                  ▼
       ┌──────────────────────────┐
       │   SEARCH_RESULTS        │
       │   (call BookingService) │
       └──────────┬───────────────┘
                  │ results found
                  ▼
       ┌──────────────────────────┐
       │   DISPLAY_OPTIONS       │
       │   (flight cards,        │
       │    hotel cards,          │
       │    AI insights)          │
       └──────────┬───────────────┘
                  │ user selects
                  ▼
       ┌──────────────────────────┐
       │   SHOW_SUMMARY          │
       │   (total, cashback,     │
       │    policy check)         │
       └──────────┬───────────────┘
                  │ user confirms
                  ▼
       ┌──────────────────────────┐
       │   EXECUTE_BOOKING       │
       │   (create trip →        │
       │    approval flow →      │
       │    issue virtual card)  │
       └──────────┬───────────────┘
                  │
                  ▼
       ┌──────────────────────────┐
       │   CONFIRMATION          │
       │   (trip #, card details,│
       │    next steps)           │
       └──────────────────────────┘
```

### Порядок уточняющих вопросов (optional slots)

Порядок фиксирован для предсказуемого UX:

1. **Обратный билет?** → `[Да, нужен обратный]` `[Нет, только туда]`
2. **Багаж?** → `[23 кг]` `[Только ручная кладь]`
3. **Нужен отель?** → `[Да, с завтраком]` `[Да, без завтрака]` `[Нет]`
4. **Трансфер из аэропорта?** → `[Да]` `[Нет, доберусь сам]`

Каждый вопрос — отдельное сообщение бота с inline-кнопками. Пользователь может ответить кнопкой или текстом.

### Контекст сессии

```json
{
  "session_id": "uuid-v4",
  "user_id": "usr_12345",
  "company_id": "comp_678",
  "role": "employee",
  "channel": "web",
  "created_at": "2026-03-10T10:00:00Z",
  "expires_at": "2026-03-10T11:00:00Z",
  "state": "ASK_OPTIONAL_SLOTS",
  "intent": "book.complex",
  "slots": {
    "origin": { "value": "MOW", "confidence": 0.98, "source": "profile_default" },
    "destination": { "value": "KZN", "confidence": 0.95, "source": "user_input" },
    "date_departure": { "value": "2026-03-10", "confidence": 0.92, "source": "user_input" },
    "date_return": { "value": null, "confidence": null, "source": null },
    "baggage": { "value": null, "confidence": null, "source": null }
  },
  "current_question": "return_ticket",
  "search_results": null,
  "selected_options": {},
  "messages_count": 4,
  "metadata": {
    "employee_id": "emp_456",
    "travel_policy_id": "pol_789"
  }
}
```

**TTL сессии**: 60 минут бездействия. После — новая сессия с вопросом «Продолжить предыдущий запрос?».

**Хранение**: Redis (горячая сессия) + PostgreSQL (история для аналитики и обучения).

---

## 1.5. Conversation Flows (детальные сценарии)

### Сценарий 1: Полный цикл бронирования

```
USER: Мне нужно в Казань на 10 марта, самолёт

BOT:  [onboarding card — если первое обращение]
      Привет! Я помогу с командировкой.
      📍 Москва → Казань, 10 марта

      Нужен обратный билет?
      [Да, нужен обратный]  [Нет, только туда]

USER: [клик: Да, нужен обратный]

BOT:  На какую дату обратный?
      [12 марта (чт)]  [13 марта (пт)]  [Другая дата]

USER: 13 марта

BOT:  Нужен ли багаж?
      [23 кг]  [Только ручная кладь]

USER: Ручная кладь

BOT:  Нужен отель в Казани (10-13 марта)?
      [Да, с завтраком]  [Да, без завтрака]  [Нет, не нужен]

USER: [клик: Да, с завтраком]

BOT:  Нужен трансфер из аэропорта?
      [Да, закажи такси]  [Нет, доберусь сам]

USER: Нет

BOT:  [typing indicator 1-2 сек]
      Нашёл варианты:

      ✈️ АВИАБИЛЕТЫ (Москва → Казань, 10 мар / Казань → Москва, 13 мар)

      [Flight Card: S7 Airlines]
      ⭐ Лучшая цена
      SVO → KZN · 08:00—09:30 · Прямой · 1ч 30м
      KZN → SVO · 18:00—19:30 · Прямой · 1ч 30м
      4 580 ₽ (туда-обратно)
      ✅ В рамках политики
      [Выбрать]

      [Flight Card: Аэрофлот]
      SVO → KZN · 14:10—15:45 · Прямой · 1ч 35м
      KZN → SVO · 20:15—21:50 · Прямой · 1ч 35м
      6 890 ₽
      ⚠️ Превышает лимит на 890 ₽
      [Выбрать]

      [Flight Card: Победа]
      VKO → KZN · 11:40—13:15 · Прямой · 1ч 35м
      KZN → VKO · 16:30—18:05 · Прямой · 1ч 35м
      3 200 ₽
      ✅ В рамках политики
      [Выбрать]

      💡 AI-совет: Цена на S7 может вырасти на ~12% завтра.
         Рекомендую забронировать сейчас.

USER: [клик: Выбрать S7]

BOT:  Отлично! S7 выбран ✓

      🏨 ОТЕЛИ (Казань, 10-13 мар, 3 ночи, с завтраком)

      [Hotel Card: Kazan Palace]
      ⭐ Рекомендую
      ★★★★ · 4.6 · 0.8 км от центра
      Завтрак включён · Wi-Fi · Фитнес
      4 200 ₽/ночь × 3 = 12 600 ₽
      ✅ В рамках политики
      [Выбрать]

      [Hotel Card: Ibis Казань]
      ★★★ · 4.1 · 1.5 км от центра
      Завтрак включён · Wi-Fi
      3 400 ₽/ночь × 3 = 10 200 ₽
      ✅ В рамках политики
      [Выбрать]

      [Показать ещё 15 вариантов]

USER: [клик: Выбрать Kazan Palace]

BOT:  Отлично! Вот итоговая сводка:

      ┌─────────────────────────────────────┐
      │ 📋 СВОДКА БРОНИРОВАНИЯ             │
      │                                     │
      │ ✈ S7 Airlines (туда-обратно)  4 580₽│
      │ 🏨 Kazan Palace (3 ночи)    12 600₽│
      │ ─────────────────────────────────── │
      │ Итого:                      17 180₽│
      │ Кэшбэк:                      +860₽│
      │                                     │
      │ ✅ Всё в рамках тревел-политики     │
      └─────────────────────────────────────┘

      [🟡 Забронировать всё]  [Изменить]

USER: [клик: Забронировать всё]

BOT:  [кнопка меняется: 🔵 Бронирую... (loading)]
      [через 2 сек: 🟢 Забронировано! ✓]

      ✅ Заявка #1248 создана и отправлена на согласование

      📋 Детали:
      • Рейс: S7 4580, SVO → KZN, 10 мар 08:00
      • Обратно: S7 4581, KZN → SVO, 13 мар 18:00
      • Отель: Kazan Palace, 10-13 мар
      • Согласующий: Алексей Петров
      • Виртуальная карта будет выпущена после согласования

      Сообщу, когда заявку одобрят! 👍
```

### Сценарий 2: Загрузка чека (OCR)

```
USER: [прикрепляет фото чека] Добавь этот чек

BOT:  [typing 1-2 сек]
      📷 Чек распознан:

      ┌─────────────────────────────────────┐
      │ 🍽 Кафе «Сказка»                   │
      │ Дата: 11.03.2026                    │
      │ Сумма: 850 ₽                        │
      │ НДС (20%): 141.67 ₽                │
      │ ИНН: 1657012345                     │
      │ ФН: 9960440300123456                │
      └─────────────────────────────────────┘

      К какой командировке отнести?
      [Казань, 10-13 мар (#1248)]
      [Екатеринбург, 5-7 мар (#1245)]
      [Другая]

USER: [клик: Казань]

BOT:  ✅ Расход 850 ₽ добавлен в авансовый отчёт по командировке #1248
      Категория: Питание
      Текущий итог отчёта: 18 030 ₽ (из лимита 25 000 ₽)
```

### Сценарий 3: Руководитель согласовывает (Telegram)

```
BOT → TELEGRAM (push):
      📋 Новая заявка на согласование

      👤 Дмитрий Иванов
      📍 Москва → Казань
      📅 10-13 марта 2026

      ✈ S7 Airlines: 4 580 ₽
      🏨 Kazan Palace (3 ночи): 12 600 ₽
      ───────────────────
      💰 Итого: 17 180 ₽
      📊 Лимит: 25 000 ₽
      ✅ В рамках политики

      [✅ Согласовать]  [❌ Отклонить]
      [💬 Комментарий]

РУКОВОДИТЕЛЬ: [клик: ✅ Согласовать]

BOT → TELEGRAM:
      ✅ Заявка #1248 согласована
      Бронирование запущено автоматически

BOT → WEB/MOBILE (Дмитрию):
      🎉 Ваша командировка в Казань согласована!
      Билеты и отель забронированы.
      💳 Виртуальная карта выпущена: •••• 4521
      Лимит: 25 000 ₽
```

---

## 1.6. API AI-агента

### POST /api/v1/chat/message

Отправка сообщения AI-агенту.

**Request:**
```json
{
  "session_id": "uuid-v4 | null",
  "message": "Мне нужно в Казань на 10 марта",
  "attachments": [
    {
      "type": "image",
      "url": "https://storage.t-komandirovka.ru/receipts/abc123.jpg",
      "mime_type": "image/jpeg"
    }
  ],
  "context": {
    "page": "home",
    "trip_id": null,
    "quick_action": null
  }
}
```

**Response (SSE stream):**
```
event: session
data: {"session_id": "sess_abc123"}

event: typing
data: {"status": "thinking"}

event: text
data: {"content": "Нашёл варианты для вас:\n"}

event: component
data: {
  "type": "flight_card",
  "data": {
    "id": "fl_001",
    "airline": "S7 Airlines",
    "airline_logo": "https://...",
    "origin": "SVO",
    "destination": "KZN",
    "departure": "2026-03-10T08:00:00",
    "arrival": "2026-03-10T09:30:00",
    "duration_minutes": 90,
    "stops": 0,
    "price": 4580,
    "currency": "RUB",
    "policy_status": "compliant",
    "badges": ["best_price"],
    "cashback": 229,
    "return_flight": {
      "departure": "2026-03-13T18:00:00",
      "arrival": "2026-03-13T19:30:00"
    }
  }
}

event: component
data: {
  "type": "ai_insight",
  "data": {
    "text": "Цена на S7 может вырасти на ~12% завтра",
    "confidence": 0.78,
    "source": "price_prediction_model"
  }
}

event: component
data: {
  "type": "quick_replies",
  "data": {
    "buttons": [
      {"id": "select_fl_001", "label": "Выбрать S7", "style": "primary"},
      {"id": "select_fl_002", "label": "Выбрать Победу", "style": "secondary"},
      {"id": "show_more", "label": "Показать ещё", "style": "ghost"}
    ]
  }
}

event: done
data: {"message_id": "msg_xyz789"}
```

### GET /api/v1/chat/history

**Query params:** `session_id`, `limit` (default 50), `before_message_id`

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Мне нужно в Казань на 10 марта",
      "timestamp": "2026-03-10T10:00:00Z",
      "attachments": []
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "Нашёл варианты...",
      "timestamp": "2026-03-10T10:00:02Z",
      "components": [
        {"type": "flight_card", "data": {...}},
        {"type": "ai_insight", "data": {...}}
      ]
    }
  ],
  "has_more": false
}
```

### POST /api/v1/chat/action

Обработка нажатия inline-кнопки.

**Request:**
```json
{
  "session_id": "sess_abc123",
  "action_id": "select_fl_001",
  "message_id": "msg_002"
}
```

### POST /api/v1/chat/feedback

**Request:**
```json
{
  "message_id": "msg_002",
  "rating": "positive",
  "comment": null
}
```

---

## 1.7. OCR Pipeline

### Обработка чеков

```
Фото чека (JPEG/PNG, до 10MB)
       │
       ▼
┌──────────────┐
│ Preprocessing│  • Deskew (выравнивание)
│              │  • Crop (обрезка)
│              │  • Contrast enhancement
│              │  • Noise reduction
└──────┬───────┘
       ▼
┌──────────────┐
│ OCR Engine   │  • Tesseract 5 / Google Vision API
│              │  • Специализированная модель для кассовых чеков РФ
└──────┬───────┘
       ▼
┌──────────────┐
│ Entity       │  Извлечение:
│ Extraction   │  • vendor_name (название)
│ (NER)        │  • date (дата)
│              │  • total (итого)
│              │  • vat (НДС)
│              │  • inn (ИНН продавца)
│              │  • fn (фискальный номер)
│              │  • items[] (позиции)
└──────┬───────┘
       ▼
┌──────────────┐
│ Validation   │  • ИНН — проверка контрольной суммы
│              │  • ФН — проверка в базе ФНС (если подключён)
│              │  • Сумма — совпадение позиций с итого
│              │  • Дата — в пределах командировки
└──────┬───────┘
       ▼
┌──────────────┐
│ Category     │  Автокатегоризация:
│ Classifier   │  • Питание, Такси, Канцелярия, Связь...
│              │  На основе vendor_name + items
└──────┬───────┘
       ▼
  Результат OCR (JSON)
```

### Модель данных OCR-результата

```json
{
  "receipt_id": "rcpt_abc123",
  "status": "recognized",
  "confidence": 0.94,
  "data": {
    "vendor_name": "Кафе «Сказка»",
    "vendor_inn": "1657012345",
    "date": "2026-03-11",
    "time": "13:45",
    "total": 850.00,
    "vat": 141.67,
    "vat_rate": 20,
    "fiscal_number": "9960440300123456",
    "items": [
      {"name": "Бизнес-ланч", "qty": 1, "price": 650.00},
      {"name": "Капучино", "qty": 1, "price": 200.00}
    ],
    "category": "food",
    "category_confidence": 0.91
  },
  "image_url": "https://storage.../rcpt_abc123.jpg",
  "needs_review": false,
  "review_reason": null
}
```

**Если confidence < 0.7**: `needs_review: true` → бот предлагает ручную корректировку.

---

## 1.8. Нефункциональные требования AI-агента

| Метрика | Требование |
|---------|-----------|
| Latency (первый токен) | < 800 мс |
| Latency (полный ответ, текст) | < 3 сек |
| Latency (с поиском билетов) | < 7 сек |
| Intent accuracy | ≥ 92% |
| Slot extraction accuracy | ≥ 88% |
| OCR accuracy (total + date) | ≥ 95% |
| Uptime | 99.9% |
| Concurrent sessions | до 10 000 |
| Session history depth | до 100 сообщений |
| Поддерживаемые языки | Русский (primary), English (secondary) |

---

# SPEC-2: БРОНИРОВАНИЕ

## 2.1. Обзор

Модуль бронирования — ядро транзакционной логики платформы. Обеспечивает поиск, сравнение, бронирование, оплату, обмен и возврат авиабилетов, ж/д билетов, отелей, такси и трансферов.

### Архитектура модуля

```
┌─────────────────────────────────────────────────────────────┐
│                     BOOKING SERVICE                          │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐│
│  │ Search       │   │ Price        │   │ Booking          ││
│  │ Aggregator   │   │ Engine       │   │ Manager          ││
│  │              │   │              │   │                  ││
│  │ • Fan-out    │   │ • Markup     │   │ • Create/Cancel  ││
│  │   queries    │   │ • Corporate  │   │ • Status FSM     ││
│  │ • Merge &    │   │   rates      │   │ • PNR mgmt       ││
│  │   deduplicate│   │ • Cashback   │   │ • Ticketing       ││
│  │ • Rank &     │   │   calc       │   │ • Voucher mgmt   ││
│  │   filter     │   │ • Policy     │   │                  ││
│  │              │   │   check      │   │                  ││
│  └──────┬───────┘   └──────┬───────┘   └────────┬─────────┘│
│         │                  │                     │          │
│  ┌──────┴──────────────────┴─────────────────────┴────────┐ │
│  │                    SUPPLIER GATEWAY                     │ │
│  │                                                         │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐          │ │
│  │  │Amadeus │ │Sirena  │ │Direct  │ │Ostrovok│          │ │
│  │  │GDS     │ │/Sabre  │ │API     │ │Hotels  │          │ │
│  │  │        │ │        │ │(S7,    │ │API     │          │ │
│  │  │        │ │        │ │Pobeda) │ │        │          │ │
│  │  └────────┘ └────────┘ └────────┘ └────────┘          │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐                     │ │
│  │  │РЖД    │ │Яндекс  │ │VIP     │                     │ │
│  │  │API     │ │Go API  │ │Lounge  │                     │ │
│  │  │        │ │(такси) │ │API     │                     │ │
│  │  └────────┘ └────────┘ └────────┘                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2.2. Поиск авиабилетов

### API: POST /api/v1/flights/search

**Request:**
```json
{
  "segments": [
    {
      "origin": "MOW",
      "destination": "KZN",
      "date": "2026-03-10",
      "time_preference": "morning"
    },
    {
      "origin": "KZN",
      "destination": "MOW",
      "date": "2026-03-13",
      "time_preference": "evening"
    }
  ],
  "passengers": [
    {
      "type": "adult",
      "employee_id": "emp_456"
    }
  ],
  "cabin_class": "economy",
  "baggage_required": false,
  "trip_id": "trip_1248",
  "company_id": "comp_678",
  "sort_by": "price_asc",
  "filters": {
    "max_price": null,
    "airlines": [],
    "max_stops": 1,
    "departure_time_from": null,
    "departure_time_to": null
  },
  "limit": 20,
  "offset": 0
}
```

**Response:**
```json
{
  "search_id": "srch_xyz789",
  "results": [
    {
      "offer_id": "off_001",
      "supplier": "sirena",
      "airline": {
        "code": "S7",
        "name": "S7 Airlines",
        "logo_url": "https://..."
      },
      "segments": [
        {
          "direction": "outbound",
          "origin": {"code": "SVO", "city": "Москва", "terminal": "B"},
          "destination": {"code": "KZN", "city": "Казань", "terminal": "1"},
          "departure": "2026-03-10T08:00:00+03:00",
          "arrival": "2026-03-10T09:30:00+03:00",
          "duration_minutes": 90,
          "stops": 0,
          "aircraft": "A320",
          "flight_number": "S7 4580",
          "cabin_class": "economy",
          "baggage": {"included_kg": 0, "hand_luggage_kg": 10}
        },
        {
          "direction": "return",
          "origin": {"code": "KZN", "city": "Казань"},
          "destination": {"code": "SVO", "city": "Москва"},
          "departure": "2026-03-13T18:00:00+03:00",
          "arrival": "2026-03-13T19:30:00+03:00",
          "duration_minutes": 90,
          "stops": 0,
          "flight_number": "S7 4581"
        }
      ],
      "pricing": {
        "total": 4580,
        "currency": "RUB",
        "base_fare": 3800,
        "taxes": 780,
        "markup": 0,
        "corporate_discount": -200,
        "cashback": 229,
        "cashback_percent": 5
      },
      "policy": {
        "status": "compliant",
        "limit": 6000,
        "overage": 0,
        "rule_id": "pol_rule_123"
      },
      "badges": ["best_price"],
      "refundable": true,
      "exchangeable": true,
      "seats_left": 14,
      "price_valid_until": "2026-03-10T23:59:59Z"
    }
  ],
  "meta": {
    "total_results": 47,
    "search_time_ms": 2340,
    "suppliers_queried": ["sirena", "amadeus", "s7_direct", "pobeda_direct"],
    "cached": false
  },
  "ai_insights": [
    {
      "type": "price_prediction",
      "text": "Цена на S7 может вырасти на ~12% завтра",
      "confidence": 0.78,
      "direction": "up",
      "percentage": 12
    }
  ]
}
```

### Алгоритм поиска (fan-out / merge)

```
1. Получить запрос
2. Определить релевантных поставщиков по маршруту:
   - MOW→KZN: Sirena, Amadeus, S7 Direct, Pobeda Direct
3. Fan-out: отправить параллельные запросы всем поставщикам
   - Timeout на каждый поставщик: 5 сек
   - Если поставщик не ответил — возвращаем остальные
4. Merge:
   - Дедупликация по (airline + flight_number + date)
   - Если один рейс из нескольких источников — минимальная цена
5. Enrich:
   - Применить корпоративные скидки (corporate_discount)
   - Рассчитать кэшбэк
   - Проверить тревел-политику (policy check)
   - Добавить AI-инсайты (price prediction)
6. Rank:
   - По умолчанию: price_asc
   - AI-ранкинг: score = price * 0.4 + policy_fit * 0.3 + convenience * 0.3
7. Return results (кэшировать на 15 минут)
```

### Кэширование

| Уровень | TTL | Ключ | Хранение |
|---------|-----|------|----------|
| Результаты поиска | 15 мин | `search:{hash(params)}` | Redis |
| Цены рейсов (волатильные) | 5 мин | `price:{offer_id}` | Redis |
| Маршруты и расписание | 24 ч | `schedule:{route}:{date}` | Redis |
| Информация об авиакомпаниях | 7 дней | `airline:{code}` | PostgreSQL + Redis |
| Информация об аэропортах | 30 дней | `airport:{code}` | PostgreSQL + Redis |

---

## 2.3. Бронирование (создание заказа)

### API: POST /api/v1/bookings

**Request:**
```json
{
  "trip_id": "trip_1248",
  "items": [
    {
      "type": "flight",
      "offer_id": "off_001",
      "search_id": "srch_xyz789",
      "passengers": [{"employee_id": "emp_456"}]
    },
    {
      "type": "hotel",
      "offer_id": "htl_002",
      "search_id": "srch_htl_456",
      "guests": [{"employee_id": "emp_456"}],
      "special_requests": "Высокий этаж, non-smoking"
    }
  ],
  "payment": {
    "method": "corporate_account",
    "virtual_card_id": null
  },
  "requester_id": "emp_456",
  "notes": null
}
```

### State Machine бронирования

```
                    ┌──────────────┐
                    │   CREATED    │
                    └──────┬───────┘
                           │ auto / manual
                           ▼
             ┌─────────────────────────────┐
             │     PENDING_APPROVAL        │
             │  (ждёт согласования)         │
             └──────┬──────────────┬───────┘
                    │              │
              approved         rejected
                    │              │
                    ▼              ▼
         ┌──────────────┐  ┌──────────────┐
         │  APPROVED    │  │  REJECTED    │
         └──────┬───────┘  └──────────────┘
                │
                │ booking confirmed by supplier
                ▼
         ┌──────────────┐
         │  CONFIRMED   │
         │ (PNR issued) │
         └──────┬───────┘
                │
                │ ticket issued / voucher issued
                ▼
         ┌──────────────┐
         │  TICKETED    │
         │ (билет       │
         │  выписан)    │
         └──────┬───────┘
                │
       ┌────────┼─────────┐
       │        │         │
       ▼        ▼         ▼
  ┌────────┐ ┌────────┐ ┌────────────┐
  │COMPLETED│ │EXCHANGED│ │CANCELLED/  │
  │(поездка │ │(обмен)  │ │REFUNDED    │
  │завершена)│ │         │ │            │
  └─────────┘ └─────────┘ └────────────┘
```

### Модель данных: Booking

```sql
CREATE TABLE bookings (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id         UUID NOT NULL REFERENCES trips(id),
  company_id      UUID NOT NULL REFERENCES companies(id),
  employee_id     UUID NOT NULL REFERENCES employees(id),
  status          VARCHAR(30) NOT NULL DEFAULT 'created',
  booking_type    VARCHAR(20) NOT NULL, -- flight, train, hotel, taxi, transfer
  
  supplier        VARCHAR(50) NOT NULL,
  supplier_ref    VARCHAR(100), -- PNR / confirmation number
  offer_snapshot  JSONB NOT NULL, -- снимок оффера на момент бронирования
  
  price_total     DECIMAL(12,2) NOT NULL,
  price_currency  VARCHAR(3) NOT NULL DEFAULT 'RUB',
  cashback_amount DECIMAL(10,2) DEFAULT 0,
  
  policy_status   VARCHAR(20), -- compliant, soft_violation, hard_violation
  policy_overage  DECIMAL(10,2) DEFAULT 0,
  
  payment_method  VARCHAR(30),
  payment_ref     VARCHAR(100),
  virtual_card_id UUID REFERENCES virtual_cards(id),
  
  booked_at       TIMESTAMPTZ,
  cancelled_at    TIMESTAMPTZ,
  cancel_reason   TEXT,
  refund_amount   DECIMAL(12,2),
  
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bookings_trip ON bookings(trip_id);
CREATE INDEX idx_bookings_company ON bookings(company_id);
CREATE INDEX idx_bookings_employee ON bookings(employee_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_created ON bookings(created_at);
```

---

## 2.4. Поиск отелей

### API: POST /api/v1/hotels/search

**Request:**
```json
{
  "city": "KZN",
  "checkin": "2026-03-10",
  "checkout": "2026-03-13",
  "guests": 1,
  "rooms": 1,
  "filters": {
    "max_price_per_night": 5000,
    "min_stars": 3,
    "breakfast_included": true,
    "wifi": true,
    "distance_km": null
  },
  "employee_id": "emp_456",
  "trip_id": "trip_1248",
  "company_id": "comp_678",
  "sort_by": "recommendation",
  "limit": 20
}
```

**Response:** аналогична авиа — массив `results[]` с `offer_id`, `pricing`, `policy`, `badges`.

### Ранкинг отелей (AI-рекомендация)

```
score = Σ (weight_i × factor_i)

Факторы:
  price_fit       (0.25) — насколько цена ниже лимита
  rating          (0.20) — рейтинг отеля (4.5/5 → 0.9)
  distance        (0.10) — расстояние до цели командировки
  history_match   (0.20) — сотрудник останавливался ранее / предпочтения
  breakfast       (0.10) — наличие завтрака
  corporate_rate  (0.15) — наличие корпоративного тарифа

Если history_match > 0.8 → badge «Рекомендую (ранее останавливался здесь)»
Если price = min(prices) → badge «Лучшая цена»
Если corporate_rate → badge «Корпоративный тариф -20%»
```

---

## 2.5. Нефункциональные требования бронирования

| Метрика | Требование |
|---------|-----------|
| Время поиска авиа (p95) | < 5 сек |
| Время поиска отелей (p95) | < 3 сек |
| Время создания бронирования | < 10 сек |
| Конкурентные поисковые запросы | до 1 000/мин |
| Точность цен | Отклонение от итоговой ≤ 1% |
| Доступность поиска | 99.9% |

---

# SPEC-3: УПРАВЛЕНИЕ КОМАНДИРОВКАМИ

## 3.1. Жизненный цикл командировки

### State Machine командировки (Trip)

```
┌───────────┐     submit      ┌───────────────────┐
│  DRAFT    │────────────────→│ PENDING_APPROVAL  │
│ (черновик)│                 │ (на согласовании) │
└───────────┘                 └────────┬──────┬───┘
      ↑                              │      │
      │ edit                   approve│      │reject
      │                              ▼      ▼
      │                     ┌──────────┐ ┌──────────┐
      └─────────────────────│ APPROVED │ │ REJECTED │
          (если отклонена   └────┬─────┘ └──────────┘
           → можно                │
           редактировать)         │ bookings confirmed
                                  ▼
                          ┌──────────────┐
                          │   BOOKED     │
                          │(забронировано)│
                          └──────┬───────┘
                                 │ departure date reached
                                 ▼
                          ┌──────────────┐
                          │  IN_PROGRESS │
                          │ (в поездке)  │
                          └──────┬───────┘
                                 │ return date passed
                                 ▼
                          ┌──────────────┐
                          │   REPORTING  │
                          │ (оформление  │
                          │  отчёта)     │
                          └──────┬───────┘
                                 │ report submitted & approved
                                 ▼
                          ┌──────────────┐
                          │  COMPLETED   │
                          │ (завершена)  │
                          └──────────────┘

Параллельные переходы:
  Любой статус → CANCELLED (по инициативе сотрудника / руководителя)
```

### Модель данных: Trip

```sql
CREATE TABLE trips (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id        UUID NOT NULL REFERENCES companies(id),
  employee_id       UUID NOT NULL REFERENCES employees(id),
  created_by        UUID NOT NULL REFERENCES users(id),
  
  status            VARCHAR(30) NOT NULL DEFAULT 'draft',
  trip_number       SERIAL, -- автоинкрементный номер внутри компании
  
  title             VARCHAR(255),
  purpose           VARCHAR(500),
  project           VARCHAR(255),
  
  destinations      JSONB NOT NULL DEFAULT '[]',
  -- [{"city": "Казань", "date_from": "2026-03-10", "date_to": "2026-03-13"}]
  
  date_start        DATE NOT NULL,
  date_end          DATE NOT NULL,
  
  budget_estimated  DECIMAL(12,2),
  budget_approved   DECIMAL(12,2),
  budget_spent      DECIMAL(12,2) DEFAULT 0,
  
  per_diem_rate     DECIMAL(10,2), -- суточные
  per_diem_days     INTEGER,
  per_diem_total    DECIMAL(10,2),
  
  policy_id         UUID REFERENCES travel_policies(id),
  policy_status     VARCHAR(20),
  
  approval_chain_id UUID REFERENCES approval_chains(id),
  approved_by       UUID REFERENCES users(id),
  approved_at       TIMESTAMPTZ,
  rejected_reason   TEXT,
  
  virtual_card_id   UUID REFERENCES virtual_cards(id),
  
  order_document_id UUID, -- приказ Т-9
  assignment_doc_id UUID, -- служебное задание
  expense_report_id UUID REFERENCES expense_reports(id),
  
  notes             TEXT,
  tags              VARCHAR(50)[],
  
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 3.2. Согласование (Approval Workflow)

### Модель цепочки согласования

```sql
CREATE TABLE approval_chains (
  id          UUID PRIMARY KEY,
  company_id  UUID NOT NULL REFERENCES companies(id),
  name        VARCHAR(255) NOT NULL,
  steps       JSONB NOT NULL,
  -- [
  --   {"order": 1, "role": "direct_manager", "auto_approve_if": "budget <= 15000"},
  --   {"order": 2, "role": "cfo", "condition": "budget > 50000"}
  -- ]
  is_active   BOOLEAN DEFAULT true,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE approval_requests (
  id              UUID PRIMARY KEY,
  trip_id         UUID NOT NULL REFERENCES trips(id),
  chain_id        UUID NOT NULL REFERENCES approval_chains(id),
  current_step    INTEGER NOT NULL DEFAULT 1,
  status          VARCHAR(20) NOT NULL DEFAULT 'pending',
  -- pending, approved, rejected, expired, delegated
  
  approver_id     UUID REFERENCES users(id),
  decided_at      TIMESTAMPTZ,
  decision        VARCHAR(10), -- approve, reject
  comment         TEXT,
  
  auto_approved   BOOLEAN DEFAULT false,
  auto_reason     VARCHAR(255),
  
  deadline_at     TIMESTAMPTZ, -- SLA дедлайн
  escalated       BOOLEAN DEFAULT false,
  escalated_to    UUID REFERENCES users(id),
  
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Логика автосогласования

```
1. Получить заявку (trip)
2. Загрузить тревел-политику компании
3. Проверить все booking items против политики:
   - Каждый item → compliant / soft_violation / hard_violation
4. Определить тип согласования:
   
   IF all items compliant AND budget <= auto_approve_limit:
     → AUTO_APPROVE (мгновенно)
     → Уведомить сотрудника
     → Запустить бронирование
   
   ELIF any item has soft_violation:
     → Отправить на согласование руководителю
     → С пометкой: «⚠️ Превышение лимита на X ₽»
   
   ELIF any item has hard_violation:
     → Отправить на согласование руководителю + CFO
     → С пометкой: «❌ Нарушение политики: бизнес-класс запрещён»
   
5. Отправить уведомление согласующему:
   - Push (мобильное приложение)
   - Telegram (inline-кнопки)
   - Email
   
6. SLA: если нет ответа за N часов → эскалация
   - Стандартный SLA: 4 рабочих часа
   - Настраиваемый по компании
```

### Правила делегирования

```
IF approver.is_on_vacation:
  delegate_to = approver.delegate
  IF delegate == null:
    escalate_to = approver.manager
```

---

## 3.3. Тревел-политика

### Модель данных

```sql
CREATE TABLE travel_policies (
  id          UUID PRIMARY KEY,
  company_id  UUID NOT NULL REFERENCES companies(id),
  name        VARCHAR(255) NOT NULL,
  version     INTEGER NOT NULL DEFAULT 1,
  is_active   BOOLEAN DEFAULT true,
  rules       JSONB NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### Структура правил (rules JSON)

```json
{
  "flight": {
    "domestic": {
      "economy": {"max_price": 15000, "enforcement": "hard"},
      "business": {
        "allowed_roles": ["c_level", "director"],
        "max_price": 50000,
        "enforcement": "hard"
      },
      "advance_booking_days": 7,
      "preferred_airlines": ["S7", "Aeroflot"]
    },
    "international": {
      "economy": {"max_price": 60000, "enforcement": "soft"},
      "business": {
        "allowed_if": "flight_duration > 6h",
        "max_price": 150000,
        "enforcement": "soft"
      }
    }
  },
  "hotel": {
    "max_price_per_night": {
      "moscow": 8000,
      "spb": 7000,
      "default": 5000
    },
    "max_stars": 4,
    "enforcement": "soft"
  },
  "per_diem": {
    "domestic": 700,
    "international": {
      "default": 2500,
      "by_country": {
        "US": 5000,
        "UK": 4500,
        "DE": 4000
      }
    }
  },
  "taxi": {
    "daily_limit": 2000,
    "allowed_classes": ["economy", "comfort"],
    "enforcement": "soft"
  },
  "total_trip_budget": {
    "auto_approve_up_to": 25000,
    "require_cfo_above": 100000
  }
}
```

### API проверки политики

**POST /api/v1/policy/check**

```json
// Request
{
  "company_id": "comp_678",
  "employee_id": "emp_456",
  "items": [
    {"type": "flight", "price": 4580, "class": "economy", "route": "MOW-KZN"},
    {"type": "hotel", "price_per_night": 4200, "city": "KZN", "nights": 3}
  ]
}

// Response
{
  "overall_status": "compliant",
  "items": [
    {
      "type": "flight",
      "status": "compliant",
      "limit": 15000,
      "actual": 4580,
      "message": null
    },
    {
      "type": "hotel",
      "status": "compliant",
      "limit": 5000,
      "actual": 4200,
      "message": null
    }
  ],
  "total_budget": {
    "estimated": 17180,
    "limit": 25000,
    "auto_approvable": true
  }
}
```

---

## 3.4. Кадровые документы

### Приказ на командировку (Т-9)

**Автогенерация по данным Trip:**

| Поле формы Т-9 | Источник данных |
|----------------|----------------|
| Наименование организации | company.legal_name |
| ФИО работника | employee.full_name |
| Структурное подразделение | employee.department |
| Должность | employee.position |
| Табельный номер | employee.personnel_number |
| Место назначения | trip.destinations[].city |
| Дата начала / окончания | trip.date_start / trip.date_end |
| Срок (календарных дней) | date_end - date_start + 1 |
| Цель командировки | trip.purpose |
| Источник финансирования | company.funding_source |
| Основание | «Служебное задание от {date}» |

**Формат выхода**: PDF (заполненная форма) + XML (для КЭДО-подписания).

### Служебное задание

Аналогичная автогенерация. Связано 1:1 с Trip.

---

## 3.5. Уведомления

### Матрица уведомлений

| Событие | Кому | Push | Telegram | Email | In-app |
|---------|------|------|----------|-------|--------|
| Заявка создана | Сотрудник | ✅ | ✅ | ❌ | ✅ |
| Ожидает согласования | Руководитель | ✅ | ✅ | ✅ | ✅ |
| Заявка согласована | Сотрудник | ✅ | ✅ | ✅ | ✅ |
| Заявка отклонена | Сотрудник | ✅ | ✅ | ✅ | ✅ |
| Бронирование подтверждено | Сотрудник | ✅ | ✅ | ✅ | ✅ |
| Изменение рейса | Сотрудник | ✅ | ✅ | ✅ | ✅ |
| Задержка рейса | Сотрудник | ✅ | ✅ | ❌ | ✅ |
| Виртуальная карта выпущена | Сотрудник | ✅ | ✅ | ❌ | ✅ |
| Транзакция по карте | Сотрудник + Руководитель (опц.) | ✅ | ❌ | ❌ | ✅ |
| Дедлайн авансового отчёта | Сотрудник | ✅ | ✅ | ✅ | ✅ |
| SLA эскалация | Руководитель + его руководитель | ✅ | ✅ | ✅ | ✅ |
| Авансовый отчёт утверждён | Сотрудник + Бухгалтер | ✅ | ✅ | ✅ | ✅ |

---

# SPEC-4: ФИНАНСОВЫЙ МОДУЛЬ

## 4.1. Виртуальная командировочная карта

### Жизненный цикл карты

```
┌──────────┐  trip approved  ┌──────────┐  activated  ┌──────────┐
│ NOT      │───────────────→│ ISSUED   │───────────→│ ACTIVE   │
│ ISSUED   │                │          │            │          │
└──────────┘                └──────────┘            └────┬─────┘
                                                         │
                                          trip ends OR   │ transactions
                                          manual freeze  │
                                                ┌────────┘
                                                ▼
                                         ┌──────────┐  report closed  ┌──────────┐
                                         │ FROZEN   │───────────────→│ CLOSED   │
                                         │          │                │          │
                                         └──────────┘                └──────────┘
```

### Модель данных

```sql
CREATE TABLE virtual_cards (
  id              UUID PRIMARY KEY,
  trip_id         UUID NOT NULL REFERENCES trips(id),
  company_id      UUID NOT NULL REFERENCES companies(id),
  employee_id     UUID NOT NULL REFERENCES employees(id),
  
  status          VARCHAR(20) NOT NULL DEFAULT 'issued',
  -- issued, active, frozen, closed
  
  card_number_masked VARCHAR(19), -- •••• •••• •••• 4521
  card_token      VARCHAR(255), -- токен для процессинга (зашифрован)
  expiry_date     DATE NOT NULL,
  
  limit_amount    DECIMAL(12,2) NOT NULL,
  spent_amount    DECIMAL(12,2) NOT NULL DEFAULT 0,
  remaining       DECIMAL(12,2) GENERATED ALWAYS AS (limit_amount - spent_amount) STORED,
  
  allowed_mcc     INTEGER[], -- разрешённые MCC-коды (категории)
  blocked_mcc     INTEGER[], -- запрещённые MCC-коды
  
  issued_at       TIMESTAMPTZ,
  activated_at    TIMESTAMPTZ,
  frozen_at       TIMESTAMPTZ,
  closed_at       TIMESTAMPTZ,
  
  tbank_card_id   VARCHAR(100), -- ID в системе Т-Банка
  
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE card_transactions (
  id              UUID PRIMARY KEY,
  virtual_card_id UUID NOT NULL REFERENCES virtual_cards(id),
  trip_id         UUID NOT NULL REFERENCES trips(id),
  
  amount          DECIMAL(12,2) NOT NULL,
  currency        VARCHAR(3) NOT NULL DEFAULT 'RUB',
  
  merchant_name   VARCHAR(255),
  merchant_mcc    INTEGER,
  category        VARCHAR(50), -- flight, hotel, taxi, food, other
  
  status          VARCHAR(20) NOT NULL, -- authorized, settled, reversed, declined
  decline_reason  VARCHAR(100),
  
  receipt_id      UUID REFERENCES receipts(id),
  
  authorized_at   TIMESTAMPTZ NOT NULL,
  settled_at      TIMESTAMPTZ,
  
  tbank_txn_ref   VARCHAR(100),
  metadata        JSONB DEFAULT '{}'
);
```

### MCC-фильтрация (по умолчанию)

| Категория | MCC-коды | Разрешено |
|-----------|----------|-----------|
| Авиакомпании | 3000-3350, 4511 | ✅ |
| Отели | 3501-3999, 7011 | ✅ |
| Ж/д транспорт | 4011, 4112 | ✅ |
| Такси | 4121 | ✅ |
| Рестораны/кафе | 5812, 5813, 5814 | ✅ |
| Продуктовые | 5411, 5422 | ✅ |
| АЗС | 5541, 5542 | ✅ (если разрешено) |
| Развлечения | 7832, 7911, 7922 | ❌ |
| Ювелирные | 5944 | ❌ |
| Казино | 7995 | ❌ |

---

## 4.2. Авансовый отчёт

### Модель данных

```sql
CREATE TABLE expense_reports (
  id              UUID PRIMARY KEY,
  trip_id         UUID NOT NULL REFERENCES trips(id),
  company_id      UUID NOT NULL REFERENCES companies(id),
  employee_id     UUID NOT NULL REFERENCES employees(id),
  
  report_number   SERIAL,
  status          VARCHAR(20) NOT NULL DEFAULT 'draft',
  -- draft, submitted, under_review, approved, rejected, exported
  
  advance_issued  DECIMAL(12,2) DEFAULT 0, -- выданный аванс
  total_expenses  DECIMAL(12,2) DEFAULT 0, -- итого расходов
  balance         DECIMAL(12,2) GENERATED ALWAYS AS (advance_issued - total_expenses) STORED,
  -- положительный = вернуть, отрицательный = доплатить
  
  per_diem_amount DECIMAL(10,2),
  per_diem_days   INTEGER,
  
  submitted_at    TIMESTAMPTZ,
  reviewed_by     UUID REFERENCES users(id),
  reviewed_at     TIMESTAMPTZ,
  exported_to_1c  BOOLEAN DEFAULT false,
  exported_at     TIMESTAMPTZ,
  
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE expense_items (
  id              UUID PRIMARY KEY,
  report_id       UUID NOT NULL REFERENCES expense_reports(id),
  
  category        VARCHAR(50) NOT NULL,
  -- flight, train, hotel, taxi, food, office_supplies, communication, other
  
  description     VARCHAR(500),
  amount          DECIMAL(12,2) NOT NULL,
  vat_amount      DECIMAL(10,2),
  vat_rate        INTEGER, -- 0, 10, 20
  
  date            DATE NOT NULL,
  vendor_name     VARCHAR(255),
  vendor_inn      VARCHAR(12),
  
  source          VARCHAR(20) NOT NULL,
  -- card_transaction, ocr_receipt, manual, booking_auto
  
  receipt_id      UUID REFERENCES receipts(id),
  booking_id      UUID REFERENCES bookings(id),
  transaction_id  UUID REFERENCES card_transactions(id),
  
  is_verified     BOOLEAN DEFAULT false,
  
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Автоматическое формирование отчёта

```
Триггер: Trip.status → REPORTING (после возвращения)

1. Собрать все card_transactions по trip_id
   → Создать expense_items с source = 'card_transaction'
   
2. Собрать все bookings по trip_id (авиа, ж/д, отели)
   → Создать expense_items с source = 'booking_auto'
   
3. Собрать все receipts (OCR-чеки) по trip_id
   → Создать expense_items с source = 'ocr_receipt'
   
4. Рассчитать суточные:
   per_diem_days = trip.date_end - trip.date_start + 1 - 
                   (дни, когда предоставлено питание)
   per_diem_amount = per_diem_days × policy.per_diem.domestic
   
5. Рассчитать итого:
   total_expenses = Σ(expense_items.amount) + per_diem_amount
   
6. Рассчитать баланс:
   balance = advance_issued - total_expenses
   IF balance > 0 → сотрудник должен вернуть
   IF balance < 0 → компания должна доплатить
   
7. Уведомить сотрудника: «Авансовый отчёт сформирован, проверьте»
   
8. Экспорт формы АО-1 в PDF
```

---

## 4.3. Возврат НДС

### Автоматический расчёт

```
Для каждого expense_item:
  1. Определить ставку НДС:
     - Авиабилет внутренний → НДС 0% (c 2025 по некоторым)
     - Авиабилет международный → НДС 0%
     - Ж/д → НДС 0% (только питание 20%)
     - Отель → НДС 20% (если включён в стоимость)
     - Питание → НДС 20%
     - Такси → НДС 20%
     
  2. Проверить наличие счёта-фактуры / кассового чека с ФН
  
  3. Рассчитать НДС к возврату:
     vat_amount = amount × vat_rate / (100 + vat_rate)
     
  4. Агрегировать по отчёту:
     total_vat = Σ(vat_amount) для items с подтверждающими документами
```

---

## 4.4. Закрывающие документы

### Типы документов

| Документ | Источник | Формат | Когда формируется |
|----------|----------|--------|-------------------|
| Приказ Т-9 | Автогенерация | PDF, XML | При создании Trip |
| Служебное задание | Автогенерация | PDF, XML | При создании Trip |
| Авансовый отчёт АО-1 | Автогенерация | PDF, XML | После завершения Trip |
| Маршрутный лист | Автогенерация | PDF | По запросу |
| Электронный билет | Поставщик (GDS) | PDF | При бронировании |
| Ваучер отеля | Поставщик | PDF | При бронировании |
| Кассовый чек | OCR / ОФД | JPEG + JSON | Во время Trip |
| Счёт-фактура | ЭДО (Диадок) | XML (УПД) | От поставщика |
| Акт оказанных услуг | ЭДО | XML | От платформы клиенту |
| Отчёт агента | Автогенерация | PDF, XML | Конец месяца |

### Хранение документов

```sql
CREATE TABLE documents (
  id              UUID PRIMARY KEY,
  trip_id         UUID REFERENCES trips(id),
  company_id      UUID NOT NULL REFERENCES companies(id),
  
  doc_type        VARCHAR(50) NOT NULL,
  doc_number      VARCHAR(100),
  doc_date        DATE,
  
  file_url        VARCHAR(500) NOT NULL, -- S3 URL
  file_size       INTEGER,
  file_format     VARCHAR(10), -- pdf, xml, jpeg
  
  signed          BOOLEAN DEFAULT false,
  signature_type  VARCHAR(20), -- simple, qualified_electronic
  signed_by       UUID REFERENCES users(id),
  signed_at       TIMESTAMPTZ,
  
  edo_status      VARCHAR(20), -- sent, delivered, signed, rejected
  edo_provider    VARCHAR(20), -- diadoc, sbis, kontur
  edo_ref         VARCHAR(100),
  
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

# SPEC-5: АНАЛИТИКА И BI

## 5.1. Архитектура данных

```
┌──────────────┐    CDC/Events    ┌──────────────┐
│  PostgreSQL  │─────────────────→│   Kafka      │
│  (OLTP)      │                  │  (events)    │
└──────────────┘                  └──────┬───────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │  ClickHouse  │
                                  │  (OLAP)      │
                                  │              │
                                  │  • trips_analytics
                                  │  • bookings_analytics
                                  │  • expenses_analytics
                                  │  • transactions_analytics
                                  └──────┬───────┘
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                       ┌──────────────┐     ┌──────────────┐
                       │ Dashboard    │     │ AI Analytics │
                       │ API          │     │ Service      │
                       │              │     │              │
                       │ /api/v1/     │     │ • Anomaly    │
                       │  analytics/* │     │   detection  │
                       │              │     │ • Forecasts  │
                       │              │     │ • Insights   │
                       └──────────────┘     └──────────────┘
```

## 5.2. Дашборд CFO

### API: GET /api/v1/analytics/dashboard

**Query params:** `company_id`, `period` (month/quarter/year), `date_from`, `date_to`, `department_id`

**Response:**
```json
{
  "period": {"from": "2026-02-01", "to": "2026-02-28"},
  "kpi": {
    "total_spend": {"value": 2400000, "delta_pct": 12, "direction": "up"},
    "savings": {"value": 340000, "delta_pct": 18, "direction": "up"},
    "trips_count": {"value": 87, "delta_abs": 8, "direction": "up"},
    "cashback": {"value": 28400, "delta_pct": 5, "direction": "up"},
    "avg_trip_cost": {"value": 27586},
    "policy_compliance_pct": {"value": 94},
    "auto_approval_pct": {"value": 68},
    "avg_booking_time_sec": {"value": 180}
  },
  "spend_by_month": [
    {"month": "2026-01", "budget": 2500000, "actual": 2140000},
    {"month": "2026-02", "budget": 2500000, "actual": 2400000}
  ],
  "spend_by_category": {
    "flights": 1368000,
    "hotels": 816000,
    "taxi": 120000,
    "food": 72000,
    "other": 24000
  },
  "top_destinations": [
    {"city": "Казань", "amount": 320000, "trips": 12},
    {"city": "Санкт-Петербург", "amount": 280000, "trips": 18},
    {"city": "Сочи", "amount": 240000, "trips": 8}
  ],
  "spend_by_department": [
    {"department": "Продажи", "amount": 890000, "budget": 1000000},
    {"department": "Маркетинг", "amount": 540000, "budget": 600000},
    {"department": "Разработка", "amount": 320000, "budget": 400000}
  ],
  "ai_insights": [
    {
      "id": "ins_001",
      "type": "anomaly",
      "severity": "warning",
      "text": "Расходы на отели в Сочи выросли на 40%. Рекомендуем пересмотреть корпоративный тариф.",
      "action": {"type": "review_policy", "params": {"city": "Сочи", "category": "hotel"}}
    },
    {
      "id": "ins_002",
      "type": "optimization",
      "severity": "info",
      "text": "30% перелётов Москва-СПб. Переход на Сапсан сэкономит ~18%.",
      "potential_saving": 50400,
      "action": {"type": "suggest_train", "params": {"route": "MOW-LED"}}
    },
    {
      "id": "ins_003",
      "type": "behavior",
      "severity": "info",
      "text": "Покупка билетов за 14+ дней экономит в среднем 22%.",
      "action": {"type": "notify_employees"}
    }
  ]
}
```

## 5.3. AI-инсайты (детальная логика)

### Типы инсайтов

| Тип | Модель | Данные | Пример |
|-----|--------|--------|--------|
| **Аномалия расходов** | Z-score анализ по категориям/направлениям | Помесячные расходы за 12 мес. | «Расходы на отели в Сочи +40%» |
| **Оптимизация маршрутов** | Сравнение альтернативных видов транспорта | Частотный анализ маршрутов + цены | «Москва-СПб на Сапсане дешевле на 18%» |
| **Поведенческий паттерн** | Регрессия advance_days vs. price | История бронирований | «Раннее бронирование экономит 22%» |
| **Прогноз бюджета** | ARIMA / Prophet на временных рядах | Историческая динамика расходов | «В Q2 ожидается +15% расходов» |
| **Fraud-детекция** | Isolation Forest / rule-based | Транзакции, геолокация | «Транзакция в Казани через 1 ч после Москвы» |

### Формула расчёта потенциальной экономии

```
optimization_saving = Σ (
  for each route with freq >= 3/month:
    current_avg_cost - alternative_avg_cost
) × annual_frequency

Пример: 
  Москва → СПб, авиа: средняя цена 5 600₽, freq = 18/мес
  Москва → СПб, Сапсан: средняя цена 4 200₽
  Потенциальная экономия = (5600 - 4200) × 18 × 12 = 302 400₽/год
```

---

## 5.4. Экспорт отчётов

| Формат | Содержание | Настройки |
|--------|-----------|-----------|
| Excel (.xlsx) | Полная таблица с фильтрами | Период, подразделение, категория |
| PDF | Визуальный отчёт с графиками | Брендированный (логотип компании) |
| CSV | Сырые данные для BI-систем | Все поля, без агрегации |
| API (JSON) | Для автоматической интеграции | Вебхуки + REST |

---

# SPEC-6: MICE (МЕРОПРИЯТИЯ)

## 6.1. Жизненный цикл мероприятия

```
BRIEFING → VENUE_SEARCH → BUDGETING → APPROVAL → 
LOGISTICS → EXECUTION → CLOSING
```

### Модель данных

```sql
CREATE TABLE mice_events (
  id              UUID PRIMARY KEY,
  company_id      UUID NOT NULL REFERENCES companies(id),
  organizer_id    UUID NOT NULL REFERENCES users(id),
  
  status          VARCHAR(20) NOT NULL DEFAULT 'briefing',
  
  title           VARCHAR(255) NOT NULL,
  type            VARCHAR(50) NOT NULL,
  -- conference, strategy_session, team_building, corporate_event, training
  
  city            VARCHAR(100),
  venue_id        UUID REFERENCES venues(id),
  
  date_start      DATE,
  date_end        DATE,
  
  participants_expected INTEGER,
  participants_confirmed INTEGER DEFAULT 0,
  
  budget_estimated DECIMAL(14,2),
  budget_approved  DECIMAL(14,2),
  budget_spent     DECIMAL(14,2) DEFAULT 0,
  
  services        JSONB DEFAULT '{}',
  -- {"venue": true, "catering": true, "equipment": true, 
  --  "accommodation": true, "transport": true, "entertainment": false}
  
  notes           TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE mice_participants (
  id              UUID PRIMARY KEY,
  event_id        UUID NOT NULL REFERENCES mice_events(id),
  employee_id     UUID REFERENCES employees(id),
  
  name            VARCHAR(255),
  email           VARCHAR(255),
  phone           VARCHAR(20),
  
  status          VARCHAR(20) DEFAULT 'invited',
  -- invited, confirmed, declined, booked, checked_in
  
  trip_id         UUID REFERENCES trips(id), -- связанная командировка
  booking_ids     UUID[], -- связанные бронирования
  
  special_needs   TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

## 6.2. Групповое бронирование

### Алгоритм массового бронирования

```
1. Организатор создаёт мероприятие + загружает список участников (Excel/CSV)
2. Система создаёт Trip для каждого участника (batch)
3. Система ищет оптимальные варианты:
   - Групповые тарифы на авиа (10+ пассажиров = запрос спецтарифа)
   - Блок номеров в отеле (10+ номеров = запрос group rate)
4. Организатор утверждает варианты
5. Система отправляет приглашения участникам (email + Telegram)
6. Каждый участник подтверждает → автоматическое бронирование
7. Real-time трекер: кто подтвердил, кто забронирован, кто прибыл
```

---

# SPEC-7: ИНТЕГРАЦИИ

## 7.1. Карта интеграций

```
┌───────────────────────────────────────────────────────────────┐
│                    Т-КОМАНДИРОВКА                              │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 INTEGRATION LAYER                        │  │
│  │                                                          │  │
│  │  ┌─────────────────┐  ┌─────────────────┐               │  │
│  │  │ БАНКОВСКИЕ       │  │ ТРЕВЕЛ-          │               │  │
│  │  │                  │  │ ПОСТАВЩИКИ       │               │  │
│  │  │ • T-Bank Core ←→ │  │ • Amadeus GDS  ← │               │  │
│  │  │ • Зарплатный  →  │  │ • Sirena       ← │               │  │
│  │  │ • Процессинг  ←→ │  │ • S7 Direct    ← │               │  │
│  │  │ • Эквайринг   ←  │  │ • РЖД API     ← │               │  │
│  │  └─────────────────┘  │ • Ostrovok     ← │               │  │
│  │                        │ • Яндекс Go   ←→ │               │  │
│  │  ┌─────────────────┐  └─────────────────┘               │  │
│  │  │ УЧЁТНЫЕ          │                                     │  │
│  │  │ СИСТЕМЫ          │  ┌─────────────────┐               │  │
│  │  │                  │  │ ДОКУМЕНТО-       │               │  │
│  │  │ • 1С:Бух      →  │  │ ОБОРОТ          │               │  │
│  │  │ • 1С:ЗУП     ←→  │  │                  │               │  │
│  │  │ • 1С:ERP     ←→  │  │ • Диадок      →  │               │  │
│  │  │ • SAP        ←→  │  │ • СБИС        →  │               │  │
│  │  │ • Oracle     ←→  │  │ • HRlink      ←→ │               │  │
│  │  └─────────────────┘  │ • Directum    ←→ │               │  │
│  │                        └─────────────────┘               │  │
│  │  ┌─────────────────┐  ┌─────────────────┐               │  │
│  │  │ АУТЕНТИФИКАЦИЯ   │  │ УВЕДОМЛЕНИЯ      │               │  │
│  │  │                  │  │                  │               │  │
│  │  │ • T-ID (SSO)  ←  │  │ • Telegram Bot → │               │  │
│  │  │ • AD/LDAP     ←  │  │ • Push (FCM)  →  │               │  │
│  │  │ • SAML 2.0    ←  │  │ • Email (SMTP)→  │               │  │
│  │  │ • OIDC        ←  │  │ • SMS         →  │               │  │
│  │  └─────────────────┘  └─────────────────┘               │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## 7.2. Интеграция с 1С

### 1С:Бухгалтерия — выгрузка авансового отчёта

**Направление:** Т-Командировка → 1С

**Формат обмена:** XML (CommerceML 2.08 совместимый)

**Маппинг полей:**

| Поле Т-Командировки | Поле 1С | Трансформация |
|---------------------|---------|---------------|
| expense_report.report_number | Номер | Прямой маппинг |
| expense_report.submitted_at | Дата | YYYY-MM-DD |
| employee.personnel_number | ФизЛицо | Поиск по табельному номеру |
| expense_report.advance_issued | АвансВыданный | Decimal |
| expense_items[].amount | СуммаРасхода | По каждой строке |
| expense_items[].vat_amount | СуммаНДС | По каждой строке |
| expense_items[].category | СтатьяЗатрат | Маппинг категорий → справочник 1С |
| expense_items[].vendor_inn | Контрагент | Поиск/создание по ИНН |
| documents[].file_url | ПрикреплённыеФайлы | Загрузка PDF |

**Маппинг категорий:**

| Категория Т-Командировки | Статья затрат 1С |
|--------------------------|------------------|
| flight | Командировочные расходы / Проезд |
| train | Командировочные расходы / Проезд |
| hotel | Командировочные расходы / Проживание |
| food | Командировочные расходы / Питание |
| taxi | Командировочные расходы / Транспорт |
| per_diem | Командировочные расходы / Суточные |
| other | Командировочные расходы / Прочее |

### 1С:ЗУП — синхронизация сотрудников

**Направление:** 1С:ЗУП ↔ Т-Командировка

```
1С:ЗУП → Т-Командировка:
  • Справочник сотрудников (ФИО, должность, подразделение, табельный номер)
  • Организационная структура (дерево подразделений)
  • Отпуска и увольнения → деактивация пользователей

Т-Командировка → 1С:ЗУП:
  • Приказ Т-9 (создание документа в ЗУП)
  • Начисление суточных (проводка)
```

**Периодичность:** Webhook (real-time) при изменениях + full sync раз в сутки (02:00).

---

## 7.3. Интеграция с Telegram

### Telegram Bot API

**Bot username:** `@t_komandirovka_bot`

**Команды:**

| Команда | Действие |
|---------|----------|
| `/start` | Привязка аккаунта (deep link с токеном) |
| `/trips` | Список активных командировок |
| `/approve` | Заявки на согласование |
| `/expenses` | Текущие расходы |
| `/help` | Список доступных команд |

**Inline-кнопки для согласования:**

```json
{
  "inline_keyboard": [
    [
      {"text": "✅ Согласовать", "callback_data": "approve:trip_1248"},
      {"text": "❌ Отклонить", "callback_data": "reject:trip_1248"}
    ],
    [
      {"text": "💬 Написать комментарий", "callback_data": "comment:trip_1248"}
    ]
  ]
}
```

**Обработка фото чека:**

```
1. Пользователь отправляет фото в бот
2. Bot получает file_id → скачивает файл
3. Загружает в S3 (storage)
4. Отправляет в OCR Pipeline
5. Возвращает результат распознавания
6. Предлагает привязать к командировке
```

---

## 7.4. REST API платформы

### Аутентификация

```
Authorization: Bearer <JWT token>

JWT payload:
{
  "sub": "usr_12345",
  "company_id": "comp_678",
  "role": "employee",
  "permissions": ["trips.create", "trips.read_own", "bookings.create"],
  "exp": 1709312400,
  "iss": "t-komandirovka"
}
```

### Ролевая модель (RBAC)

| Право | Сотрудник | Руководитель | Тревел-менеджер | Бухгалтер | CFO/Admin |
|-------|-----------|-------------|-----------------|-----------|-----------|
| trips.create | ✅ (свои) | ✅ (свои + подчинённые) | ✅ (все) | ❌ | ✅ (все) |
| trips.read | ✅ (свои) | ✅ (подразделение) | ✅ (все) | ✅ (все) | ✅ (все) |
| trips.approve | ❌ | ✅ | ❌ | ❌ | ✅ |
| bookings.create | ✅ (свои) | ✅ | ✅ | ❌ | ✅ |
| expenses.submit | ✅ (свои) | ✅ (свои) | ❌ | ❌ | ❌ |
| expenses.approve | ❌ | ✅ | ❌ | ✅ | ✅ |
| analytics.view | ❌ | ✅ (подразделение) | ✅ (все) | ✅ (финансы) | ✅ (все) |
| policy.manage | ❌ | ❌ | ✅ | ❌ | ✅ |
| users.manage | ❌ | ❌ | ❌ | ❌ | ✅ |

### Версионирование API

```
/api/v1/...    — текущая стабильная
/api/v2/...    — следующая (при breaking changes)

Заголовок: X-API-Version: 2026-03-01
Deprecation header: Sunset: Sat, 01 Sep 2026 00:00:00 GMT
```

### Rate Limiting

| Тариф | Лимит | Окно |
|-------|-------|------|
| Free | 100 req/min | Скользящее |
| Pro | 1 000 req/min | Скользящее |
| Enterprise | 10 000 req/min | Скользящее |

**Заголовки ответа:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1709312460
```

### Вебхуки

**POST /api/v1/webhooks** — регистрация

```json
{
  "url": "https://client.example.com/webhook",
  "events": [
    "trip.created",
    "trip.approved",
    "trip.rejected",
    "booking.confirmed",
    "booking.cancelled",
    "expense_report.submitted",
    "expense_report.approved",
    "card.transaction"
  ],
  "secret": "whsec_abc123..."
}
```

**Формат webhook payload:**
```json
{
  "id": "evt_abc123",
  "type": "trip.approved",
  "created": "2026-03-10T10:05:00Z",
  "data": {
    "trip_id": "trip_1248",
    "approved_by": "usr_789",
    "company_id": "comp_678"
  },
  "signature": "sha256=..."
}
```

---

# SPEC-8: ИНФРАСТРУКТУРА

## 8.1. Архитектура развёртывания

```
┌───────────────────────────────────────────────────────────────────┐
│                        KUBERNETES CLUSTER                          │
│                                                                    │
│  ┌─── INGRESS ────────────────────────────────────────────────┐   │
│  │  nginx-ingress / Envoy                                      │   │
│  │  TLS termination, rate limiting, WAF                        │   │
│  └────────┬───────────────────────────────────────────────────┘   │
│           │                                                        │
│  ┌────────┴───────────────────────────────────────────────────┐   │
│  │                     SERVICE MESH                            │   │
│  │                                                             │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │   │
│  │  │ API      │ │ Booking  │ │ Trip     │ │ Finance  │     │   │
│  │  │ Gateway  │ │ Service  │ │ Service  │ │ Service  │     │   │
│  │  │ (BFF)    │ │          │ │          │ │          │     │   │
│  │  │ 3 pods   │ │ 5 pods   │ │ 3 pods   │ │ 3 pods   │     │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │   │
│  │                                                             │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │   │
│  │  │ AI       │ │ Analytics│ │ Document │ │ Notifi-  │     │   │
│  │  │ Agent    │ │ Service  │ │ Service  │ │ cation   │     │   │
│  │  │          │ │          │ │          │ │ Service  │     │   │
│  │  │ 5 pods   │ │ 2 pods   │ │ 2 pods   │ │ 3 pods   │     │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │   │
│  │                                                             │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │   │
│  │  │ MICE     │ │ Policy   │ │ Auth     │                   │   │
│  │  │ Service  │ │ Service  │ │ Service  │                   │   │
│  │  │ 2 pods   │ │ 2 pods   │ │ 3 pods   │                   │   │
│  │  └──────────┘ └──────────┘ └──────────┘                   │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌─── DATA LAYER ─────────────────────────────────────────────┐   │
│  │                                                             │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │   │
│  │  │PostgreSQL│ │ Redis    │ │ClickHouse│ │ Kafka    │     │   │
│  │  │ (primary)│ │ Cluster  │ │ (OLAP)   │ │ Cluster  │     │   │
│  │  │ + replica│ │ 3 nodes  │ │ 2 shards │ │ 3 brokers│     │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │   │
│  │                                                             │   │
│  │  ┌──────────┐ ┌──────────┐                                 │   │
│  │  │ S3       │ │ Elastic- │                                 │   │
│  │  │ (MinIO)  │ │ search   │                                 │   │
│  │  │ documents│ │ (logs)   │                                 │   │
│  │  └──────────┘ └──────────┘                                 │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

## 8.2. Стек технологий

| Слой | Технология | Обоснование |
|------|-----------|-------------|
| **Frontend (Web)** | React 19 + TypeScript + Tailwind CSS | Стандарт, large ecosystem, SSR с Next.js |
| **Frontend (Mobile)** | React Native / Flutter | Кросс-платформенность iOS/Android |
| **API Gateway** | Kong / Envoy | Rate limiting, auth, routing |
| **BFF** | Node.js (Fastify) | Быстрый SSE-стриминг для AI-чата |
| **Backend Services** | Go (основные) + Python (AI/ML) | Go: производительность; Python: ML-экосистема |
| **AI/LLM** | YandexGPT / fine-tuned LLaMA | Российская LLM + возможность self-hosted |
| **OCR** | Tesseract 5 + custom model | On-premise, конфиденциальность данных |
| **БД (OLTP)** | PostgreSQL 16 | Надёжность, JSON-поддержка, PG-расширения |
| **БД (OLAP)** | ClickHouse | Быстрая аналитика на больших объёмах |
| **Кэш** | Redis 7 (Cluster) | Sessions, search cache, rate limiting |
| **Очереди** | Apache Kafka | Event sourcing, CDC, async processing |
| **Объектное хранилище** | S3-совместимое (MinIO / Yandex S3) | Документы, чеки, PDF |
| **Поиск (full-text)** | Elasticsearch 8 | Поиск по документам, логирование |
| **Контейнеризация** | Docker + Kubernetes | Стандарт для микросервисов |
| **CI/CD** | GitLab CI / GitHub Actions | Автоматические пайплайны |
| **Мониторинг** | Prometheus + Grafana | Метрики, алерты |
| **Логирование** | ELK Stack (Elasticsearch + Logstash + Kibana) | Централизованные логи |
| **Трейсинг** | Jaeger / OpenTelemetry | Distributed tracing |

## 8.3. Безопасность

### Шифрование

| Уровень | Механизм |
|---------|----------|
| В транзите | TLS 1.3 (все внешние соединения) |
| В покое (БД) | AES-256 (прозрачное шифрование PostgreSQL) |
| Карточные данные | PCI DSS Level 1 (токенизация через Т-Банк) |
| Персональные данные | ФЗ-152 (хранение в РФ), маскирование в логах |
| Межсервисная связь | mTLS (mutual TLS) |
| Секреты | HashiCorp Vault |

### Аутентификация и авторизация

```
Сотрудник (web/mobile)
       │
       ▼
┌──────────────┐
│ T-ID / OIDC  │  SSO через T-Bank ID или корпоративный SSO
└──────┬───────┘
       │ auth code
       ▼
┌──────────────┐
│ Auth Service │  Выпуск JWT (access + refresh)
│              │  Access token TTL: 15 мин
│              │  Refresh token TTL: 7 дней
└──────┬───────┘
       │ JWT
       ▼
┌──────────────┐
│ API Gateway  │  Валидация JWT, проверка permissions
└──────────────┘
```

### Аудит

```sql
CREATE TABLE audit_log (
  id          BIGSERIAL PRIMARY KEY,
  timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  user_id     UUID,
  company_id  UUID,
  action      VARCHAR(100) NOT NULL, -- trip.create, booking.confirm, etc.
  resource    VARCHAR(50),
  resource_id UUID,
  ip_address  INET,
  user_agent  VARCHAR(500),
  details     JSONB,
  result      VARCHAR(20) -- success, denied, error
);

-- Партиционирование по месяцам, хранение 5 лет
CREATE INDEX idx_audit_user ON audit_log(user_id, timestamp);
CREATE INDEX idx_audit_company ON audit_log(company_id, timestamp);
CREATE INDEX idx_audit_action ON audit_log(action, timestamp);
```

## 8.4. Мониторинг и SLA

### Ключевые метрики мониторинга

| Метрика | Алерт (warning) | Алерт (critical) |
|---------|-----------------|-------------------|
| API latency (p95) | > 500 мс | > 2 000 мс |
| Error rate (5xx) | > 0.5% | > 2% |
| CPU usage | > 70% | > 90% |
| Memory usage | > 75% | > 90% |
| DB connections | > 70% pool | > 90% pool |
| Kafka lag | > 1000 messages | > 10000 messages |
| Disk usage | > 70% | > 85% |
| SSL certificate expiry | < 30 дней | < 7 дней |

### SLA по тарифам

| Метрика | Free | Pro | Enterprise |
|---------|------|-----|-----------|
| Uptime | 99.0% | 99.5% | 99.9% |
| Max downtime/month | 7.3 ч | 3.6 ч | 43 мин |
| Response time (p95) | < 2 сек | < 1 сек | < 500 мс |
| Support response | 24 ч | 4 ч | 1 ч |
| Data backup | Ежедневно | Ежедневно | Каждые 6 ч |
| Disaster recovery | 24 ч | 8 ч | 2 ч |

### Backup-стратегия

```
PostgreSQL:
  • WAL-G streaming backup → S3
  • Full backup: ежедневно 03:00 MSK
  • Point-in-time recovery: до 7 дней
  • Geo-replica: второй ДЦ

Redis:
  • RDB snapshot: каждые 15 мин
  • AOF: each write (для критичных данных)

S3 (документы):
  • Versioning enabled
  • Cross-region replication
  • Lifecycle: архивация > 1 года → Cold storage

ClickHouse:
  • Incremental backup: ежедневно
  • Retention: 3 года детальных, 10 лет агрегированных
```

## 8.5. Масштабирование

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: booking-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: booking-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 65
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Pods
        value: 3
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
```

### Расчёт нагрузки (целевая)

| Параметр | MVP (3 мес.) | Year 1 | Year 2 |
|----------|-------------|--------|--------|
| Активных компаний | 200 | 2 000 | 8 000 |
| Активных пользователей | 5 000 | 50 000 | 200 000 |
| Бронирований/день | 500 | 5 000 | 20 000 |
| Поисковых запросов/день | 2 000 | 20 000 | 80 000 |
| AI-сообщений/день | 3 000 | 30 000 | 120 000 |
| Транзакций по картам/день | 200 | 2 000 | 8 000 |
| Документов/день | 500 | 5 000 | 20 000 |
| Пиковый RPS | 50 | 500 | 2 000 |

---

# ПРИЛОЖЕНИЯ

## A. Глоссарий технических терминов

| Термин | Определение |
|--------|------------|
| **SSE** | Server-Sent Events — протокол стриминга данных от сервера к клиенту |
| **PNR** | Passenger Name Record — запись бронирования в GDS |
| **MCC** | Merchant Category Code — код категории торговой точки |
| **CDC** | Change Data Capture — отслеживание изменений в БД |
| **BFF** | Backend for Frontend — серверный слой под конкретный клиент |
| **mTLS** | Mutual TLS — двусторонняя аутентификация |
| **WAL** | Write-Ahead Log — журнал транзакций PostgreSQL |
| **HPA** | Horizontal Pod Autoscaler — автомасштабирование в Kubernetes |

## B. Зависимости между модулями

```
AI Agent ──→ Booking Service ──→ Supplier Gateway
   │              │
   │              ▼
   │         Trip Service ──→ Approval Service
   │              │                │
   │              ▼                ▼
   │         Finance Service ──→ T-Bank Core API
   │              │
   │              ▼
   └────→ Document Service ──→ 1С Integration
              │                    │
              ▼                    ▼
         Analytics Service    ЭДО (Диадок)
```

## C. Миграция данных (для клиентов, переходящих с других систем)

| Сущность | Формат импорта | Маппинг |
|----------|---------------|---------|
| Сотрудники | CSV / Excel / 1С:ЗУП API | ФИО, должность, подразделение, паспорт |
| Оргструктура | CSV / AD/LDAP sync | Дерево подразделений |
| Тревел-политика | JSON-конфигурация | Лимиты, правила, цепочки |
| Историческая аналитика | CSV / Excel | Расходы за последние 12 мес. |

---

> **Статус документа:** Draft v1.0
> **Авторы:** Product & Engineering Team
> **Дата создания:** 1 марта 2026
> **Связанные документы:** [PRD](./prd.md) · [UX/UI Design](./ux-ui-design.md) · [Market Analysis](./market-analysis.md) · [Investor Deck](./investor-deck.md) · [Design Prompt](./design-prompt.md)

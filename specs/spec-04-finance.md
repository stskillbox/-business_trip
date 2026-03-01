# SPEC-04: Модуль «Финансы»

> **Платформа:** Т-Командировка — AI-платформа управления корпоративными поездками  
> **Модуль:** Finance Module  
> **Версия:** 1.0  
> **Дата:** 01.03.2026  
> **Статус:** Draft  
> **Автор:** Product & Engineering  

---

## Содержание

1. [Обзор модуля](#1-обзор-модуля)
2. [Виртуальная командировочная карта](#2-виртуальная-командировочная-карта)
3. [Оплата и расчёты](#3-оплата-и-расчёты)
4. [Суточные (Per Diem)](#4-суточные-per-diem)
5. [Кэшбэк и экономия](#5-кэшбэк-и-экономия)
6. [НДС и налоговый учёт](#6-ндс-и-налоговый-учёт)
7. [Закрывающие документы](#7-закрывающие-документы)
8. [Сверка (Reconciliation)](#8-сверка-reconciliation)
9. [Отчётность](#9-отчётность)
10. [API Reference](#10-api-reference)
11. [Безопасность](#11-безопасность)
12. [Метрики](#12-метрики)

---

## 1. Обзор модуля

### 1.1 Назначение

Модуль «Финансы» — ключевой дифференциатор платформы Т-Командировка. Ни один конкурент на российском рынке (Smartway, Яндекс Командировки, Аэроклуб, OneTwoTrip, Trivio) не предоставляет **встроенные банковские инструменты** внутри тревел-платформы.

Т-Командировка — единственный продукт, где банковский и тревел-слои объединены:

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   КОНКУРЕНТЫ                     Т-КОМАНДИРОВКА                      │
│                                                                      │
│   ┌───────────┐  ┌──────────┐    ┌──────────────────────────────┐    │
│   │  Тревел-  │  │  Банк    │    │  Тревел + Банк = ЕДИНОЕ     │    │
│   │  платформа│  │  (отдельн)│    │                              │    │
│   │           │  │          │    │  Виртуальные карты           │    │
│   │  Smartway │  │  Сбер    │    │  Кэшбэк до 10%              │    │
│   │  Яндекс   │  │  Альфа   │    │  Кредитные линии             │    │
│   │  Аэроклуб │  │  ВТБ     │    │  Отсрочка платежа            │    │
│   │           │  │          │    │  Зарплата + суточные          │    │
│   └───────────┘  └──────────┘    │  Автоматический НДС           │    │
│                                  │  Закрывающие документы        │    │
│   Два продукта, нет связи       └──────────────────────────────┘    │
│                                  Один продукт, полная интеграция     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Ключевое ценностное предложение

| # | Возможность | Конкуренты | Т-Командировка |
|---|------------|------------|----------------|
| 1 | Виртуальная карта на каждую командировку | Нет ни у кого | ✅ Автовыпуск при одобрении поездки |
| 2 | Кэшбэк за бронирования | Только OneTwoTrip (до 5%) | ✅ До 5% авиа, до 10% отели |
| 3 | Отсрочка платежа | Нет ни у кого | ✅ До 30 дней, 0% для Enterprise |
| 4 | Кредитная линия | Нет ни у кого | ✅ До 50 млн ₽ |
| 5 | Суточные на зарплатную карту | Нет ни у кого | ✅ Через зарплатный проект Т-Банка |
| 6 | Автовозврат НДС | Smartway, Аэроклуб (частично) | ✅ Полная автоматизация |
| 7 | Закрывающие документы через ЭДО | Частично | ✅ Автогенерация + Диадок / СБИС |

### 1.3 Компоненты модуля

```
┌─────────────────────────────────────────────────────────────────┐
│                     МОДУЛЬ «ФИНАНСЫ»                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │  Виртуальные  │  │   Платежи и   │  │   Суточные    │       │
│  │    карты      │  │   расчёты     │  │   (Per Diem)  │       │
│  │               │  │               │  │               │       │
│  │ • Выпуск      │  │ • Корп. счёт  │  │ • Расчёт      │       │
│  │ • Лимиты      │  │ • Отсрочка    │  │ • Начисление  │       │
│  │ • MCC-фильтр  │  │ • Кред. линия │  │ • Налоги      │       │
│  │ • Транзакции  │  │ • Холдирование│  │ • Конфиг.     │       │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘       │
│          │                  │                  │               │
│          ▼                  ▼                  ▼               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   Кэшбэк и   │  │    НДС и     │  │  Закрывающие  │       │
│  │   экономия    │  │   налоги     │  │  документы    │       │
│  │               │  │               │  │               │       │
│  │ • Начисление  │  │ • Расчёт НДС │  │ • Акты        │       │
│  │ • Геймификация│  │ • Возмещение  │  │ • Счета-ф.    │       │
│  │ • Лидерборд  │  │ • Отчётность  │  │ • УПД         │       │
│  │ • Бейджи     │  │ • Экспорт     │  │ • ЭДО         │       │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘       │
│          │                  │                  │               │
│          ▼                  ▼                  ▼               │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                    СВЕРКА И ОТЧЁТНОСТЬ               │       │
│  │  • Ежедневная сверка транзакций                      │       │
│  │  • Закрытие командировки (аванс vs. факт)           │       │
│  │  • Финансовые отчёты (Excel, PDF, CSV, API)         │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Зависимости от внутренних систем Т-Банка

| Система | API | Назначение |
|---------|-----|------------|
| T-Bank Card Issuing | Internal gRPC | Выпуск и управление виртуальными картами |
| T-Bank Processing Center | Webhook (HTTPS) | Уведомления о транзакциях в реальном времени |
| T-Bank Corporate Accounts | Internal REST | Операции по расчётному счёту компании |
| T-Bank Credit Engine | Internal gRPC | Оценка кредитоспособности, кредитные линии |
| T-Bank Payroll | Internal REST | Начисление суточных на зарплатную карту |
| T-Bank EDO Gateway | REST | Отправка документов через Диадок / СБИС |
| T-Bank KYC/AML | Internal gRPC | Проверки при выпуске карт и кредитовании |

---

## 2. Виртуальная командировочная карта

### 2.1 Концепция

Виртуальная командировочная карта — отдельная виртуальная карта Visa/Mastercard, выпускаемая автоматически при одобрении заявки на командировку. Карта привязана к конкретной поездке, имеет лимит равный бюджету поездки и категорийные ограничения по MCC-кодам.

**Отличие от обычной корпоративной карты:**

| Параметр | Корпоративная карта | Командировочная виртуальная карта |
|----------|--------------------|---------------------------------|
| Выпуск | Один раз, вручную | Автоматически на каждую поездку |
| Лимит | Общий, на месяц | = бюджет конкретной поездки |
| Срок действия | 3-5 лет | Даты командировки + 1 день |
| Категории | Все | Только разрешённые (transport, hotel, meals) |
| Привязка | К сотруднику | К командировке → к авансовому отчёту |
| Отчётность | Ручная | Автоматическая |

### 2.2 Жизненный цикл карты (State Machine)

```
                    ┌─────────────┐
                    │  REQUESTED  │ ← Заявка на командировку одобрена
                    └──────┬──────┘
                           │
                    T-Bank Card Issuing API
                           │
                    ┌──────▼──────┐
                    │   ISSUED    │ ← Карта выпущена, данные получены
                    └──────┬──────┘
                           │
                    Дата начала командировки (или ручная активация)
                           │
                    ┌──────▼──────┐
              ┌────►│   ACTIVE    │◄──── Основное рабочее состояние
              │     └──┬─────┬───┘
              │        │     │
              │   Fraud │     │ Окончание командировки
              │   Запрос│     │ Ручная блокировка
              │   сотруд│     │
              │        │     │
              │   ┌────▼─────▼───┐
              │   │   BLOCKED    │ ← Транзакции запрещены
              │   └──┬───────┬───┘
              │      │       │
              │  Разблок.    │ Закрытие поездки
              │  (admin)     │
              └──────┘       │
                      ┌──────▼──────┐
                      │   CLOSED    │ ← Финальное состояние
                      └─────────────┘
```

**Правила переходов:**

| Из | В | Триггер | Автоматический? |
|----|---|---------|:-:|
| REQUESTED | ISSUED | Ответ T-Bank Card Issuing API | Да |
| ISSUED | ACTIVE | Наступление даты начала командировки | Да |
| ISSUED | ACTIVE | Ручная активация администратором | Нет |
| ACTIVE | BLOCKED | Окончание командировки (trip_end_date + 1 день) | Да |
| ACTIVE | BLOCKED | Подозрительная транзакция (fraud detection) | Да |
| ACTIVE | BLOCKED | Запрос сотрудника (потеря данных) | Нет |
| ACTIVE | BLOCKED | Запрос администратора | Нет |
| BLOCKED | ACTIVE | Разблокировка администратором | Нет |
| BLOCKED | CLOSED | Закрытие командировки (reconciliation завершён) | Да |
| ISSUED | CLOSED | Отмена командировки | Да |

### 2.3 Интеграция с T-Bank Card Processing

#### Выпуск карты

```
Т-Командировка                 T-Bank Card Issuing
─────────────                  ────────────────────

     │                                │
     │  CreateVirtualCard(request)    │
     │───────────────────────────────►│
     │                                │  Проверка лимитов компании
     │                                │  KYC/AML проверка
     │                                │  Генерация PAN, CVV
     │  VirtualCardCreated(response)  │
     │◄───────────────────────────────│
     │                                │
     │  card_id: "vc_a1b2c3d4"       │
     │  pan_masked: "****4521"        │
     │  expiry: "03/26"              │
     │  bin: "553691"                │
     │                                │
```

#### Обработка транзакций (Real-time)

```
Торговая        Процессинг       Т-Командировка
 точка          T-Bank           (webhook)
────────        ──────────       ──────────────

   │                │                  │
   │ POS-терминал   │                  │
   │───────────────►│                  │
   │                │                  │
   │                │  1. Авторизация  │
   │                │  ──────────────  │
   │                │  Проверка лимита │
   │                │                  │
   │                │  Authorization   │
   │                │  Request         │
   │                │─────────────────►│
   │                │                  │
   │                │                  │  2. Проверка MCC
   │                │                  │  Проверка остатка
   │                │                  │  Проверка статуса карты
   │                │                  │
   │                │  APPROVE/DECLINE │
   │                │◄─────────────────│
   │                │                  │
   │  Результат     │                  │
   │◄───────────────│                  │
   │                │                  │
   │                │  3. Settlement   │
   │                │  (T+1..T+3)      │
   │                │─────────────────►│
   │                │                  │  Обновление
   │                │                  │  spent_amount
   │                │                  │  Привязка к trip
   │                │                  │  Маппинг MCC →
   │                │                  │  категория
```

#### Маппинг MCC-кодов → категории расходов

| MCC диапазон | MCC коды | Категория | Описание |
|---|---|---|---|
| 3000–3999 | Авиакомпании | TRANSPORT | Авиабилеты |
| 4011 | РЖД | TRANSPORT | Ж/д билеты |
| 4111–4131 | Транспорт (наземный) | TRANSPORT | Автобусы, трамваи, метро |
| 4121 | Такси, лимузины | TAXI | Такси, трансферы |
| 4784 | Платные дороги | TRANSPORT | Toll roads |
| 7011–7012 | Отели, мотели | ACCOMMODATION | Проживание |
| 7032–7033 | Кемпинги, спортивные лагеря | ACCOMMODATION | Проживание (альтернатива) |
| 5811–5814 | Рестораны, фастфуд | MEALS | Питание |
| 5411 | Продуктовые магазины | MEALS | Питание (супермаркеты) |
| 5912 | Аптеки | OTHER | Лекарства |
| 5999 | Прочие розничные | OTHER | Разное |

### 2.4 Модель данных

```sql
-- Виртуальные командировочные карты
CREATE TABLE virtual_cards (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id               VARCHAR(64) NOT NULL,        -- ID в системе T-Bank
    trip_request_id       UUID NOT NULL REFERENCES trip_requests(id),
    employee_id           UUID NOT NULL REFERENCES employees(id),
    company_id            UUID NOT NULL REFERENCES companies(id),

    status                VARCHAR(20) NOT NULL DEFAULT 'REQUESTED'
                          CHECK (status IN (
                              'REQUESTED', 'ISSUED', 'ACTIVE', 'BLOCKED', 'CLOSED'
                          )),

    card_number_masked    VARCHAR(19),                  -- "****4521"
    card_bin              VARCHAR(8),                   -- BIN карты
    expiry_month          SMALLINT,
    expiry_year           SMALLINT,

    limit_amount          DECIMAL(15,2) NOT NULL,       -- Лимит = бюджет поездки
    spent_amount          DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    remaining_amount      DECIMAL(15,2) GENERATED ALWAYS AS (limit_amount - spent_amount) STORED,
    currency              VARCHAR(3) NOT NULL DEFAULT 'RUB',

    category_restrictions JSONB NOT NULL DEFAULT '["transport","accommodation","meals","taxi"]',
    mcc_whitelist         JSONB,                        -- Конкретные разрешённые MCC
    mcc_blacklist         JSONB,                        -- Запрещённые MCC

    issued_at             TIMESTAMPTZ,
    activated_at          TIMESTAMPTZ,
    blocked_at            TIMESTAMPTZ,
    blocked_reason        VARCHAR(255),
    closed_at             TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_trip_request FOREIGN KEY (trip_request_id)
        REFERENCES trip_requests(id) ON DELETE RESTRICT
);

CREATE INDEX idx_virtual_cards_trip ON virtual_cards(trip_request_id);
CREATE INDEX idx_virtual_cards_employee ON virtual_cards(employee_id);
CREATE INDEX idx_virtual_cards_status ON virtual_cards(status);
CREATE INDEX idx_virtual_cards_company ON virtual_cards(company_id);

-- Транзакции по карте
CREATE TABLE card_transactions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id                 UUID NOT NULL REFERENCES virtual_cards(id),
    trip_request_id         UUID NOT NULL REFERENCES trip_requests(id),
    tbank_transaction_id    VARCHAR(64) NOT NULL UNIQUE, -- ID в процессинге T-Bank

    amount                  DECIMAL(15,2) NOT NULL,
    original_amount         DECIMAL(15,2),               -- Если в иностранной валюте
    currency                VARCHAR(3) NOT NULL DEFAULT 'RUB',
    original_currency       VARCHAR(3),

    merchant_name           VARCHAR(255),
    merchant_city           VARCHAR(128),
    merchant_country        VARCHAR(3),                   -- ISO 3166-1 alpha-3
    merchant_category_code  VARCHAR(4) NOT NULL,          -- MCC

    expense_category        VARCHAR(20) NOT NULL
                            CHECK (expense_category IN (
                                'TRANSPORT', 'ACCOMMODATION', 'MEALS', 'TAXI', 'OTHER'
                            )),

    description             TEXT,
    receipt_url             VARCHAR(512),                  -- URL скана чека (OCR)
    receipt_status          VARCHAR(20) DEFAULT 'NONE'
                            CHECK (receipt_status IN (
                                'NONE', 'UPLOADED', 'OCR_PROCESSING', 'OCR_DONE', 'VERIFIED'
                            )),

    status                  VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                            CHECK (status IN (
                                'PENDING', 'AUTHORIZED', 'SETTLED', 'REVERSED', 'DISPUTED'
                            )),

    authorization_code      VARCHAR(12),
    is_approved             BOOLEAN NOT NULL DEFAULT true, -- false = отклонённая транзакция

    transaction_at          TIMESTAMPTZ NOT NULL,
    settled_at              TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_card_tx_card ON card_transactions(card_id);
CREATE INDEX idx_card_tx_trip ON card_transactions(trip_request_id);
CREATE INDEX idx_card_tx_status ON card_transactions(status);
CREATE INDEX idx_card_tx_date ON card_transactions(transaction_at);
CREATE INDEX idx_card_tx_mcc ON card_transactions(merchant_category_code);
```

### 2.5 Движок категорийных ограничений

#### Архитектура принятия решения в реальном времени

```
Webhook от процессинга
        │
        ▼
┌───────────────────┐
│  Parse MCC code   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐     ┌──────────────────────┐
│  Карта активна?   │─No─►│ DECLINE: CARD_BLOCKED │
└────────┬──────────┘     └──────────────────────┘
         │ Yes
         ▼
┌───────────────────┐     ┌──────────────────────┐
│  MCC в blacklist? │─Yes►│ DECLINE: MCC_BLOCKED  │
└────────┬──────────┘     └──────────────────────┘
         │ No
         ▼
┌───────────────────┐     ┌──────────────────────┐
│  MCC в whitelist? │─No─►│ DECLINE: MCC_NOT_ALLOWED│
│  (если задан)     │     └──────────────────────┘
└────────┬──────────┘
         │ Yes (или whitelist не задан)
         ▼
┌───────────────────┐     ┌──────────────────────┐
│  MCC → категория  │─?──►│ Категория = OTHER     │
│  в маппинге?      │     │ (если не в маппинге)  │
└────────┬──────────┘     └──────────────────────┘
         │
         ▼
┌───────────────────┐     ┌──────────────────────┐
│  Категория в      │─No─►│ DECLINE: CATEGORY_NOT │
│  restrictions?    │     │         _ALLOWED      │
└────────┬──────────┘     └──────────────────────┘
         │ Yes
         ▼
┌───────────────────┐     ┌──────────────────────┐
│  remaining_amount │─No─►│ DECLINE: LIMIT_EXCEEDED│
│  >= amount?       │     └──────────────────────┘
└────────┬──────────┘
         │ Yes
         ▼
┌───────────────────┐
│    APPROVE        │
└───────────────────┘
```

#### Конфигурация ограничений по компаниям

```json
{
  "company_id": "comp_xyz789",
  "card_policy": {
    "allowed_categories": ["transport", "accommodation", "meals", "taxi"],
    "mcc_blacklist": [
      {"mcc": "5813", "description": "Бары и ночные клубы"},
      {"mcc": "5921", "description": "Алкогольные магазины"},
      {"mcc": "7995", "description": "Азартные игры"},
      {"mcc": "7922", "description": "Театры, развлечения"},
      {"mcc": "5944", "description": "Ювелирные магазины"}
    ],
    "mcc_whitelist_override": null,
    "single_transaction_limit": 50000.00,
    "daily_transaction_limit": 150000.00,
    "require_receipt_above": 5000.00,
    "auto_block_on_trip_end": true,
    "block_delay_after_trip_hours": 24
  }
}
```

---

## 3. Оплата и расчёты

### 3.1 Способы оплаты

```
┌─────────────────────────────────────────────────────────────────┐
│                    СПОСОБЫ ОПЛАТЫ                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    Основной способ                     │
│  │ 1. КОРПОРАТИВНЫЙ    │    Прямое списание с расчётного счёта  │
│  │    СЧЁТ             │    компании в Т-Банке                  │
│  │    (settlement acc.) │    Используется для бронирований       │
│  └─────────────────────┘                                        │
│                                                                 │
│  ┌─────────────────────┐    Для расходов во время поездки       │
│  │ 2. ВИРТУАЛЬНАЯ      │    Лимит = бюджет поездки              │
│  │    КАРТА             │    MCC-ограничения                    │
│  │                     │    Автоматическая привязка к trip       │
│  └─────────────────────┘                                        │
│                                                                 │
│  ┌─────────────────────┐    Для личных/смешанных поездок        │
│  │ 3. ЛИЧНАЯ КАРТА     │    Возмещение после командировки       │
│  │    СОТРУДНИКА       │    Через зарплатный проект             │
│  └─────────────────────┘                                        │
│                                                                 │
│  ┌─────────────────────┐    Для Enterprise-клиентов             │
│  │ 4. КРЕДИТНАЯ        │    Отсрочка до 30 дней                 │
│  │    ЛИНИЯ            │    Лимит до 50 млн ₽                   │
│  └─────────────────────┘                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Платёжный flow при бронировании

```
Сотрудник      AI-агент       Policy      Payment       Провайдер
──────────     ────────       ──────      ───────       ─────────

    │              │             │            │              │
    │  "Забронируй │             │            │              │
    │   S7 и       │             │            │              │
    │   Holiday    │             │            │              │
    │   Inn"       │             │            │              │
    │─────────────►│             │            │              │
    │              │             │            │              │
    │              │ checkPolicy │            │              │
    │              │────────────►│            │              │
    │              │             │            │              │
    │              │  APPROVED   │            │              │
    │              │◄────────────│            │              │
    │              │             │            │              │
    │              │         initiatePayment  │              │
    │              │────────────────────────►│              │
    │              │             │            │              │
    │              │             │     holdFunds (корп. счёт │
    │              │             │     или кредитная линия)  │
    │              │             │            │──────┐       │
    │              │             │            │      │       │
    │              │             │            │◄─────┘       │
    │              │             │            │              │
    │              │             │     HOLD_CONFIRMED       │
    │              │◄────────────────────────│              │
    │              │             │            │              │
    │              │         bookWithProvider │              │
    │              │───────────────────────────────────────►│
    │              │             │            │              │
    │              │         ticket/voucher issued           │
    │              │◄───────────────────────────────────────│
    │              │             │            │              │
    │              │         settlePayment   │              │
    │              │────────────────────────►│              │
    │              │             │            │              │
    │              │             │     SETTLED              │
    │              │◄────────────────────────│              │
    │              │             │            │              │
    │  "Готово!    │             │            │              │
    │   Билет S7   │             │            │              │
    │   + Holiday  │             │            │              │
    │   Inn"       │             │            │              │
    │◄─────────────│             │            │              │
```

### 3.3 Модель данных платежей

```sql
-- Платежи
CREATE TABLE payments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id),
    trip_request_id     UUID REFERENCES trip_requests(id),
    booking_id          UUID REFERENCES bookings(id),

    payment_method      VARCHAR(20) NOT NULL
                        CHECK (payment_method IN (
                            'CORPORATE_ACCOUNT', 'VIRTUAL_CARD',
                            'PERSONAL_CARD', 'CREDIT_LINE'
                        )),

    amount              DECIMAL(15,2) NOT NULL,
    currency            VARCHAR(3) NOT NULL DEFAULT 'RUB',
    vat_amount          DECIMAL(15,2) DEFAULT 0.00,
    vat_rate            DECIMAL(5,2),

    status              VARCHAR(20) NOT NULL DEFAULT 'INITIATED'
                        CHECK (status IN (
                            'INITIATED', 'HOLD', 'SETTLED', 'REFUNDED',
                            'PARTIALLY_REFUNDED', 'FAILED', 'CANCELLED'
                        )),

    provider_name       VARCHAR(128),
    provider_reference  VARCHAR(128),
    description         TEXT,

    hold_at             TIMESTAMPTZ,
    settled_at          TIMESTAMPTZ,
    refunded_at         TIMESTAMPTZ,
    due_date            DATE,                   -- Для отсрочки платежа
    is_deferred         BOOLEAN DEFAULT false,  -- Отложенный платёж?

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_payments_company ON payments(company_id);
CREATE INDEX idx_payments_trip ON payments(trip_request_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_due_date ON payments(due_date) WHERE is_deferred = true;
```

### 3.4 Отсрочка платежа (Payment Deferral)

Отсрочка платежа — ключевое конкурентное преимущество, доступное только в банковской экосистеме.

| Параметр | Free | Pro | Enterprise |
|----------|------|-----|------------|
| Доступность | Нет | Да | Да |
| Максимальный срок | — | 14 дней | 30 дней |
| Процентная ставка | — | 0% (14 дней) | 0% (30 дней) |
| Лимит на компанию | — | 5 млн ₽ | 50 млн ₽ |
| Автопогашение | — | Да | Да |
| Штраф за просрочку | — | 0,1%/день | 0,05%/день |

#### Процесс отсрочки

```
День 0:  Бронирование → HOLD на корп. счёт или кредитную линию
         Статус: DEFERRED

День 1-14 (Pro) / 1-30 (Enterprise):
         0% — беспроцентный период
         Уведомления: за 3 дня, за 1 день до due_date

Due date: Автоматическое списание с расчётного счёта компании
         Статус: SETTLED

Просрочка:
  +1 день:  Push-уведомление + email финансовому директору
  +3 дня:   SMS-уведомление + повторное списание
  +7 дней:  Звонок менеджера
  +14 дней: Начисление штрафных процентов
  +30 дней: Блокировка новых бронирований
  +60 дней: Передача в юридический отдел
```

#### Модель данных отсрочки

```sql
CREATE TABLE deferred_payments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id          UUID NOT NULL REFERENCES payments(id),
    company_id          UUID NOT NULL REFERENCES companies(id),

    principal_amount    DECIMAL(15,2) NOT NULL,
    interest_rate       DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    penalty_rate        DECIMAL(5,4) NOT NULL DEFAULT 0.0010,  -- 0.1%/день

    grace_period_days   INT NOT NULL,             -- 14 или 30
    due_date            DATE NOT NULL,
    actual_payment_date DATE,

    accrued_interest    DECIMAL(15,2) DEFAULT 0.00,
    accrued_penalty     DECIMAL(15,2) DEFAULT 0.00,
    total_due           DECIMAL(15,2) GENERATED ALWAYS AS
                        (principal_amount + accrued_interest + accrued_penalty) STORED,

    status              VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
                        CHECK (status IN (
                            'ACTIVE', 'SETTLED', 'OVERDUE', 'DEFAULTED'
                        )),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.5 Кредитная линия

```
┌──────────────────────────────────────────────────────────────────┐
│                     КРЕДИТНАЯ ЛИНИЯ                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Тип:           Возобновляемая (revolving)                       │
│  Макс. лимит:   50 000 000 ₽ (Enterprise)                       │
│  Ставка:        Ключевая ЦБ + 3-5% годовых                      │
│  Грейс-период:  30 дней (0%)                                    │
│  Погашение:     Ежемесячно, автосписание с расч. счёта           │
│  Обеспечение:   Без залога (до 10 млн ₽)                        │
│                 Поручительство учредителя (>10 млн ₽)            │
│                                                                  │
│  Процесс выдачи:                                                │
│                                                                  │
│  1. Компания подаёт заявку через личный кабинет                  │
│  2. T-Bank Credit Engine → автоматический скоринг                │
│     • Финансовая отчётность (интеграция с ФНС через API)        │
│     • История операций по расчётному счёту                       │
│     • Кредитная история (БКИ)                                   │
│     • Объём бронирований на платформе                            │
│  3. Решение: < 1 часа (автоматически) или < 1 дня (ручной)      │
│  4. Активация: мгновенная после подписания оферты (ЭЦП)         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

```sql
CREATE TABLE credit_lines (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id),
    tbank_credit_id     VARCHAR(64) NOT NULL,

    approved_limit      DECIMAL(15,2) NOT NULL,
    used_amount         DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    available_amount    DECIMAL(15,2) GENERATED ALWAYS AS
                        (approved_limit - used_amount) STORED,
    currency            VARCHAR(3) NOT NULL DEFAULT 'RUB',

    interest_rate       DECIMAL(5,4) NOT NULL,    -- Годовая ставка
    grace_period_days   INT NOT NULL DEFAULT 30,
    penalty_rate        DECIMAL(5,4) NOT NULL,

    status              VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN (
                            'PENDING', 'APPROVED', 'ACTIVE', 'SUSPENDED', 'CLOSED'
                        )),

    approved_at         TIMESTAMPTZ,
    activated_at        TIMESTAMPTZ,
    next_statement_date DATE,
    expires_at          DATE,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE credit_line_statements (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    credit_line_id      UUID NOT NULL REFERENCES credit_lines(id),
    statement_period    DATE NOT NULL,            -- Первый день месяца

    opening_balance     DECIMAL(15,2) NOT NULL,
    total_charges       DECIMAL(15,2) NOT NULL,
    total_payments      DECIMAL(15,2) NOT NULL,
    interest_charged    DECIMAL(15,2) NOT NULL,
    closing_balance     DECIMAL(15,2) NOT NULL,
    minimum_payment     DECIMAL(15,2) NOT NULL,
    due_date            DATE NOT NULL,

    status              VARCHAR(20) NOT NULL DEFAULT 'GENERATED'
                        CHECK (status IN ('GENERATED', 'SENT', 'PAID', 'OVERDUE')),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 4. Суточные (Per Diem)

### 4.1 Движок расчёта суточных

#### Таблица ставок (Россия)

| Тип города | Города | Ставка по умолчанию | Налоговый порог |
|------------|--------|--------------------:|:--:|
| Tier 1 | Москва, Санкт-Петербург | 1 200 ₽/сут | 700 ₽/сут |
| Tier 2 | Екатеринбург, Казань, Новосибирск, Нижний Новгород, Красноярск, Самара | 900 ₽/сут | 700 ₽/сут |
| Tier 3 | Остальные города | 700 ₽/сут | 700 ₽/сут |

#### Таблица ставок (Международные)

| Регион/Страна | Ставка по умолчанию | Налоговый порог |
|---------------|--------------------:|:--:|
| Турция | 3 500 ₽/сут | 2 500 ₽/сут |
| Китай | 4 000 ₽/сут | 2 500 ₽/сут |
| ОАЭ | 5 000 ₽/сут | 2 500 ₽/сут |
| Узбекистан | 2 500 ₽/сут | 2 500 ₽/сут |
| Германия | 4 500 ₽/сут | 2 500 ₽/сут |
| США | 5 500 ₽/сут | 2 500 ₽/сут |
| Прочие | По нормативам Минфина | 2 500 ₽/сут |

> Ставки по умолчанию соответствуют нормативам Минфина РФ. Компания может переопределить ставки в настройках тревел-политики — в этом случае сумма выше налогового порога облагается НДФЛ и страховыми взносами.

#### Алгоритм расчёта

```python
def calculate_per_diem(trip):
    """
    Расчёт суточных по правилам:
    - День прибытия: 50% ставки (конфигурируется)
    - Полные дни: 100% ставки
    - День отъезда: 50% ставки (конфигурируется)
    - Если однодневная командировка: 100% (конфигурируется: 100% | 50% | 0%)
    """
    company_config = get_company_per_diem_config(trip.company_id)
    destination = get_destination(trip.destination_city, trip.destination_country)
    rate = get_rate(destination, company_config)
    tax_threshold = get_tax_threshold(destination)

    arrival_date = trip.start_date
    departure_date = trip.end_date
    total_days = (departure_date - arrival_date).days + 1

    if total_days == 1:
        factor = company_config.single_day_factor  # default: 1.0
        gross_amount = rate * factor
    else:
        arrival_factor = company_config.arrival_day_factor    # default: 0.5
        departure_factor = company_config.departure_day_factor # default: 0.5
        full_days = total_days - 2

        gross_amount = (
            rate * arrival_factor +
            rate * full_days +
            rate * departure_factor
        )

    taxable_amount = max(0, gross_amount - tax_threshold * total_days)
    tax_free_amount = gross_amount - taxable_amount

    return PerDiemCalculation(
        total_days=total_days,
        daily_rate=rate,
        gross_amount=gross_amount,
        tax_free_amount=tax_free_amount,
        taxable_amount=taxable_amount,
        ndfl_amount=taxable_amount * 0.13,
        insurance_amount=taxable_amount * 0.30,
    )
```

#### Пример расчёта

```
Командировка: Москва → Казань, 10-14 марта (5 дней)

Ставка Tier 2 (Казань): 900 ₽/сут
Налоговый порог (Россия): 700 ₽/сут

День 1 (10.03, прибытие):   900 × 0.5 = 450 ₽
День 2 (11.03, полный):     900 × 1.0 = 900 ₽
День 3 (12.03, полный):     900 × 1.0 = 900 ₽
День 4 (13.03, полный):     900 × 1.0 = 900 ₽
День 5 (14.03, отъезд):     900 × 0.5 = 450 ₽
                             ─────────────────
Итого gross:                           3 600 ₽

Налоговый порог: 700 × 5 =            3 500 ₽
Taxable:         3 600 - 3 500 =         100 ₽
НДФЛ (13%):     100 × 0.13 =             13 ₽
Страховые (30%): 100 × 0.30 =            30 ₽

К выплате сотруднику: 3 600 - 13 =    3 587 ₽
```

### 4.2 Автоматическое начисление суточных

```
Одобрение заявки                T-Bank Payroll API
────────────────                ──────────────────

       │                              │
       │  1. trip_approved event      │
       │──────────┐                   │
       │          │                   │
       │  2. calculate_per_diem()     │
       │          │                   │
       │  3. Проверка: дата начала    │
       │     - 1 день                 │
       │          │                   │
       │  4. Создать payroll order    │
       │──────────────────────────────►
       │                              │
       │                              │  Зачисление на
       │                              │  зарплатную карту
       │                              │  сотрудника
       │                              │
       │  5. payment_confirmed        │
       │◄──────────────────────────────
       │                              │
       │  6. Push-уведомление         │
       │     сотруднику:              │
       │     "Суточные 3 587 ₽        │
       │      зачислены на карту      │
       │      ****1234"               │
       │                              │
```

#### Модель данных суточных

```sql
CREATE TABLE per_diem_calculations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_request_id     UUID NOT NULL REFERENCES trip_requests(id),
    employee_id         UUID NOT NULL REFERENCES employees(id),
    company_id          UUID NOT NULL REFERENCES companies(id),

    destination_city    VARCHAR(128) NOT NULL,
    destination_country VARCHAR(3) NOT NULL DEFAULT 'RUS',
    city_tier           VARCHAR(10),

    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL,
    total_days          INT NOT NULL,

    daily_rate          DECIMAL(10,2) NOT NULL,
    arrival_factor      DECIMAL(3,2) NOT NULL DEFAULT 0.50,
    departure_factor    DECIMAL(3,2) NOT NULL DEFAULT 0.50,

    gross_amount        DECIMAL(15,2) NOT NULL,
    tax_threshold       DECIMAL(10,2) NOT NULL,
    tax_free_amount     DECIMAL(15,2) NOT NULL,
    taxable_amount      DECIMAL(15,2) NOT NULL,
    ndfl_amount         DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    insurance_amount    DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    net_amount          DECIMAL(15,2) NOT NULL,   -- К выплате

    payment_status      VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                        CHECK (payment_status IN (
                            'PENDING', 'SCHEDULED', 'PAID', 'FAILED', 'CANCELLED'
                        )),
    payment_date        DATE,
    payroll_reference   VARCHAR(64),              -- ID в T-Bank Payroll

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 4.3 Конфигурация суточных по компаниям

```json
{
  "company_id": "comp_xyz789",
  "per_diem_config": {
    "use_default_rates": false,
    "custom_rates": {
      "RUS": {
        "tier_1": 1500.00,
        "tier_2": 1200.00,
        "tier_3": 900.00
      },
      "TUR": 4000.00,
      "CHN": 5000.00,
      "default_international": 3500.00
    },
    "arrival_day_factor": 0.5,
    "departure_day_factor": 0.5,
    "single_day_factor": 1.0,
    "credit_timing": "1_DAY_BEFORE",
    "credit_method": "SALARY_CARD",
    "require_approval_for_override": true
  }
}
```

---

## 5. Кэшбэк и экономия

### 5.1 Движок кэшбэка

#### Ставки по тарифным планам

| Категория | Free | Pro | Enterprise |
|-----------|:----:|:---:|:----------:|
| Авиабилеты | 1% | 3% | 5% |
| Отели | 2% | 5% | 10% |
| Ж/д билеты | 1% | 3% | 5% |
| Такси | 0% | 2% | 3% |
| MICE | — | 3% | 5% |

#### Правила начисления

```
Бронирование                  Завершение поездки
────────────                  ──────────────────

     │                              │
     │  Booking confirmed           │
     │──────────┐                   │
     │          │                   │
     │  Начислить 50%               │
     │  кэшбэка                    │
     │  (статус: ACCRUED)           │
     │          │                   │
     │          ▼                   │
     │  cashback_part_1             │
     │  = amount × rate × 0.5      │
     │                              │
     │                              │  Trip completed
     │                              │  + no disputes
     │                              │  + no cancellations
     │                              │──────────┐
     │                              │          │
     │                              │  Начислить 50%
     │                              │  кэшбэка
     │                              │  (статус: CONFIRMED)
     │                              │          │
     │                              │          ▼
     │                              │  cashback_part_2
     │                              │  = amount × rate × 0.5
     │                              │
     │                              │  Зачисление:
     │                              │  → Корпоративный счёт (default)
     │                              │  → или split с сотрудником
```

#### Модель данных кэшбэка

```sql
CREATE TABLE cashback_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id),
    employee_id         UUID REFERENCES employees(id),
    trip_request_id     UUID REFERENCES trip_requests(id),
    booking_id          UUID REFERENCES bookings(id),

    booking_category    VARCHAR(20) NOT NULL
                        CHECK (booking_category IN (
                            'FLIGHT', 'HOTEL', 'TRAIN', 'TAXI', 'MICE', 'OTHER'
                        )),
    booking_amount      DECIMAL(15,2) NOT NULL,
    cashback_rate       DECIMAL(5,4) NOT NULL,
    cashback_amount     DECIMAL(15,2) NOT NULL,

    accrual_phase       VARCHAR(10) NOT NULL
                        CHECK (accrual_phase IN ('PHASE_1', 'PHASE_2')),
    -- PHASE_1: 50% при бронировании, PHASE_2: 50% после завершения

    status              VARCHAR(20) NOT NULL DEFAULT 'ACCRUED'
                        CHECK (status IN (
                            'ACCRUED', 'CONFIRMED', 'CREDITED', 'CANCELLED', 'REVERSED'
                        )),

    credit_target       VARCHAR(20) NOT NULL DEFAULT 'CORPORATE_ACCOUNT'
                        CHECK (credit_target IN (
                            'CORPORATE_ACCOUNT', 'EMPLOYEE_CARD', 'SPLIT'
                        )),
    split_company_pct   DECIMAL(5,2) DEFAULT 100.00,
    split_employee_pct  DECIMAL(5,2) DEFAULT 0.00,

    credited_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_cashback_company ON cashback_transactions(company_id);
CREATE INDEX idx_cashback_trip ON cashback_transactions(trip_request_id);
CREATE INDEX idx_cashback_status ON cashback_transactions(status);
```

### 5.2 Геймификация: экономия сотрудника

Механизм мотивации сотрудников выбирать бюджетные варианты: если сотрудник бронирует вариант дешевле бюджетного лимита, разница делится между компанией и сотрудником.

#### Правила распределения экономии

```
Бюджет на отель (по политике):  8 000 ₽/ночь
Сотрудник выбрал:               5 500 ₽/ночь
Экономия:                       2 500 ₽/ночь × 3 ночи = 7 500 ₽

Распределение (по умолчанию):
  Компании (70%):    7 500 × 0.70 = 5 250 ₽  → возврат в бюджет
  Сотруднику (30%):  7 500 × 0.30 = 2 250 ₽  → бонус на личную карту
```

#### Лидерборд и бейджи

```sql
CREATE TABLE employee_savings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id         UUID NOT NULL REFERENCES employees(id),
    company_id          UUID NOT NULL REFERENCES companies(id),
    trip_request_id     UUID NOT NULL REFERENCES trip_requests(id),

    budget_amount       DECIMAL(15,2) NOT NULL,
    actual_amount       DECIMAL(15,2) NOT NULL,
    savings_amount      DECIMAL(15,2) GENERATED ALWAYS AS
                        (budget_amount - actual_amount) STORED,

    company_share_pct   DECIMAL(5,2) NOT NULL DEFAULT 70.00,
    employee_share_pct  DECIMAL(5,2) NOT NULL DEFAULT 30.00,
    employee_bonus      DECIMAL(15,2) NOT NULL,

    bonus_status        VARCHAR(20) NOT NULL DEFAULT 'CALCULATED'
                        CHECK (bonus_status IN (
                            'CALCULATED', 'APPROVED', 'CREDITED', 'CANCELLED'
                        )),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE employee_badges (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id         UUID NOT NULL REFERENCES employees(id),
    badge_type          VARCHAR(50) NOT NULL,
    badge_name          VARCHAR(128) NOT NULL,
    description         TEXT,
    earned_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Доступные бейджи:**

| Бейдж | Условие | Описание |
|-------|---------|----------|
| `first_save` | Первая экономия | «Первая экономия» |
| `save_10k` | Накопленная экономия > 10 000 ₽ | «Экономист» |
| `save_50k` | Накопленная экономия > 50 000 ₽ | «Суперэкономист» |
| `save_100k` | Накопленная экономия > 100 000 ₽ за квартал | «Сэкономил 100К за квартал» |
| `streak_3` | 3 командировки подряд с экономией | «Серия экономии» |
| `top_saver_month` | #1 в рейтинге за месяц | «Лучший эконом месяца» |
| `budget_hero` | 10+ командировок в рамках бюджета | «Герой бюджета» |

---

## 6. НДС и налоговый учёт

### 6.1 Расчёт НДС

#### Ставки НДС по категориям

| Категория | Ставка НДС | Основание |
|-----------|:----------:|-----------|
| Внутренние авиаперелёты | 0% | пп. 4 п. 1 ст. 164 НК РФ |
| Международные авиаперелёты | 0% | пп. 4 п. 1 ст. 164 НК РФ |
| Ж/д билеты (внутренние) | 0% | пп. 9.3 п. 1 ст. 164 НК РФ |
| Проживание (отели) | 20% | п. 3 ст. 164 НК РФ |
| Питание (рестораны) | 20% | п. 3 ст. 164 НК РФ |
| Аренда автомобиля | 20% | п. 3 ст. 164 НК РФ |
| Такси | 20% | п. 3 ст. 164 НК РФ |
| Услуги платформы (сервисный сбор) | 20% | п. 3 ст. 164 НК РФ |

#### Автоматическое извлечение НДС

```
Поступление документа от провайдера
              │
              ▼
┌─────────────────────────┐
│  1. OCR / парсинг       │
│     электронного        │
│     документа           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  2. Извлечение полей:   │
│     - Сумма с НДС       │
│     - Сумма НДС         │
│     - Ставка НДС        │
│     - ИНН поставщика     │
│     - Номер и дата с/ф   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  3. Валидация:          │
│     - Арифметическая    │
│       проверка          │
│     - Проверка ИНН      │
│       (ЕГРЮЛ)           │
│     - Сопоставление     │
│       с бронированием   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  4. Формирование        │
│     записи в книге      │
│     покупок             │
└─────────────────────────┘
```

### 6.2 Модель данных НДС

```sql
CREATE TABLE vat_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id),
    trip_request_id     UUID REFERENCES trip_requests(id),
    booking_id          UUID REFERENCES bookings(id),
    payment_id          UUID REFERENCES payments(id),

    document_type       VARCHAR(20) NOT NULL
                        CHECK (document_type IN (
                            'INVOICE', 'ACT', 'UPD', 'RECEIPT', 'TICKET'
                        )),
    document_number     VARCHAR(64),
    document_date       DATE NOT NULL,

    supplier_inn        VARCHAR(12) NOT NULL,
    supplier_kpp        VARCHAR(9),
    supplier_name       VARCHAR(255) NOT NULL,

    amount_with_vat     DECIMAL(15,2) NOT NULL,
    amount_without_vat  DECIMAL(15,2) NOT NULL,
    vat_amount          DECIMAL(15,2) NOT NULL,
    vat_rate            DECIMAL(5,2) NOT NULL,

    expense_category    VARCHAR(20) NOT NULL,
    is_deductible       BOOLEAN NOT NULL DEFAULT true,

    verification_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                        CHECK (verification_status IN (
                            'PENDING', 'VERIFIED', 'REJECTED', 'MANUAL_REVIEW'
                        )),

    source_document_url VARCHAR(512),
    purchase_book_entry BOOLEAN DEFAULT false,

    tax_period          VARCHAR(7),    -- формат: "2026-Q1"
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_vat_company ON vat_records(company_id);
CREATE INDEX idx_vat_period ON vat_records(tax_period);
CREATE INDEX idx_vat_status ON vat_records(verification_status);
```

### 6.3 Подготовка к возмещению НДС

Автоматическая подготовка пакета документов для возмещения НДС:

| Шаг | Действие | Автоматизация |
|:---:|----------|:-------------:|
| 1 | Сбор счетов-фактур и УПД от провайдеров | ✅ Автоматически |
| 2 | Проверка реквизитов поставщиков по ЕГРЮЛ | ✅ Автоматически |
| 3 | Сопоставление с бронированиями | ✅ Автоматически |
| 4 | Арифметическая проверка сумм НДС | ✅ Автоматически |
| 5 | Формирование записей книги покупок | ✅ Автоматически |
| 6 | Экспорт для налоговой декларации | ✅ XML + Excel |
| 7 | Подписание и отправка через ЭДО | ✅ Диадок / СБИС |

---

## 7. Закрывающие документы

### 7.1 Типы документов

| Тип | Код | Описание | Когда формируется |
|-----|-----|----------|-------------------|
| Акт выполненных работ | ACT | Подтверждение оказания услуг | После оказания услуги |
| Счёт-фактура | INVOICE_VAT | Документ с выделенным НДС | Вместе с актом |
| Счёт на оплату | PAYMENT_INVOICE | Документ для предоплаты | При бронировании |
| УПД | UPD | Универсальный передаточный документ | Заменяет акт + с/ф |
| Ваучер | VOUCHER | Подтверждение бронирования | При бронировании |
| Маршрутная квитанция | ITINERARY | Авиа/ж/д маршрутная квитанция | При выписке билета |

### 7.2 Автоматическая генерация

```
Событие "услуга оказана"
         │
         ▼
┌───────────────────────┐
│  Template Engine       │
│                       │
│  Входные данные:      │
│  • Реквизиты компании │
│  • Реквизиты платформы│
│  • Сумма, НДС         │
│  • Перечень услуг      │
│  • Период оказания     │
│                       │
│  Шаблоны:             │
│  • act_template.docx  │
│  • upd_template.xlsx  │
│  • invoice_template   │
│                       │
│  Брендирование:       │
│  • Логотип компании   │
│  • Печать и подпись    │
│    (электронные)       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  Электронная подпись   │
│  (КЭП / УКЭП)         │
│                       │
│  Подписание через      │
│  T-Bank Certificate    │
│  Authority             │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  Отправка через ЭДО   │
│                       │
│  ┌─────────┐          │
│  │ Диадок  │ ← API    │
│  └─────────┘          │
│  ┌─────────┐          │
│  │  СБИС   │ ← API    │
│  └─────────┘          │
│  ┌─────────┐          │
│  │  Контур │ ← API    │
│  └─────────┘          │
└───────────────────────┘
```

### 7.3 Модель данных документов

```sql
CREATE TABLE closing_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id),
    trip_request_id     UUID REFERENCES trip_requests(id),
    booking_id          UUID REFERENCES bookings(id),
    payment_id          UUID REFERENCES payments(id),

    document_type       VARCHAR(30) NOT NULL
                        CHECK (document_type IN (
                            'ACT', 'INVOICE_VAT', 'PAYMENT_INVOICE',
                            'UPD', 'VOUCHER', 'ITINERARY'
                        )),

    document_number     VARCHAR(64) NOT NULL,
    document_date       DATE NOT NULL,

    issuer_inn          VARCHAR(12) NOT NULL,
    issuer_kpp          VARCHAR(9),
    issuer_name         VARCHAR(255) NOT NULL,
    recipient_inn       VARCHAR(12) NOT NULL,
    recipient_kpp       VARCHAR(9),
    recipient_name      VARCHAR(255) NOT NULL,

    amount_with_vat     DECIMAL(15,2) NOT NULL,
    amount_without_vat  DECIMAL(15,2) NOT NULL,
    vat_amount          DECIMAL(15,2) NOT NULL,
    vat_rate            DECIMAL(5,2) NOT NULL,
    currency            VARCHAR(3) NOT NULL DEFAULT 'RUB',

    description         TEXT,

    file_url            VARCHAR(512),
    file_format         VARCHAR(10),    -- PDF, XML, DOCX
    file_size_bytes     BIGINT,

    signature_status    VARCHAR(20) NOT NULL DEFAULT 'UNSIGNED'
                        CHECK (signature_status IN (
                            'UNSIGNED', 'SIGNED_BY_ISSUER', 'SIGNED_BY_BOTH',
                            'REJECTED'
                        )),

    edo_provider        VARCHAR(20),    -- DIADOK, SBIS, KONTUR
    edo_document_id     VARCHAR(128),
    edo_status          VARCHAR(20) DEFAULT 'NOT_SENT'
                        CHECK (edo_status IN (
                            'NOT_SENT', 'SENT', 'DELIVERED', 'ACCEPTED',
                            'REJECTED', 'ERROR'
                        )),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_docs_company ON closing_documents(company_id);
CREATE INDEX idx_docs_trip ON closing_documents(trip_request_id);
CREATE INDEX idx_docs_type ON closing_documents(document_type);
CREATE INDEX idx_docs_date ON closing_documents(document_date);
```

### 7.4 Архив документов

| Параметр | Значение |
|----------|----------|
| Хранилище | S3-совместимое (T-Bank Object Storage) |
| Срок хранения | Минимум 5 лет (требование НК РФ, ст. 23) |
| Полнотекстовый поиск | Elasticsearch, индексация при загрузке |
| Резервирование | Geo-distributed, 3 реплики |
| Доступ | Бухгалтер + Администратор (RBAC) |
| Шифрование | AES-256 at rest, TLS 1.3 in transit |
| Аудит | Все обращения логируются |

---

## 8. Сверка (Reconciliation)

### 8.1 Ежедневная сверка

Ежедневный процесс сопоставления данных из трёх источников:

```
┌──────────────────────────────────────────────────────────────────┐
│                    ЕЖЕДНЕВНАЯ СВЕРКА (02:00 MSK)                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Источник 1:           Источник 2:           Источник 3:        │
│  Транзакции по         Бронирования          Платежи             │
│  виртуальным картам    на платформе           провайдерам        │
│                                                                  │
│  ┌──────────┐          ┌──────────┐          ┌──────────┐       │
│  │ card_    │          │ bookings │          │ provider │       │
│  │ transact.│          │          │          │ payments │       │
│  └─────┬────┘          └─────┬────┘          └─────┬────┘       │
│        │                     │                     │            │
│        └─────────────┬───────┘─────────────────────┘            │
│                      │                                          │
│                      ▼                                          │
│              ┌───────────────┐                                  │
│              │  Matching     │                                  │
│              │  Engine       │                                  │
│              └───────┬───────┘                                  │
│                      │                                          │
│           ┌──────────┼──────────┐                               │
│           ▼          ▼          ▼                               │
│     ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│     │ MATCHED  │ │ UNMATCHED│ │ ANOMALY  │                     │
│     │          │ │          │ │          │                     │
│     │ Транзак. │ │ Транзак. │ │ Сумма ≠  │                     │
│     │ совпадает│ │ без      │ │ Дубликат │                     │
│     │ с бронир.│ │ бронир.  │ │ Подозрит.│                     │
│     └──────────┘ └──────────┘ └──────────┘                     │
│                                                                  │
│     Результат → reconciliation_report (daily)                   │
│     Аномалии → alert в Slack / email бухгалтеру                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 8.2 Сверка при закрытии командировки

```
Командировка завершена
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│                СВЕРКА АВАНСА И ФАКТА                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Аванс (budget):                                          │
│    Лимит виртуальной карты          35 000 ₽              │
│    + Суточные выплаченные            3 587 ₽              │
│    = Итого аванс                    38 587 ₽              │
│                                                            │
│  Факт (actual):                                           │
│    Транзакции по карте:                                    │
│      Отель Holiday Inn              15 200 ₽              │
│      Такси (3 поездки)               2 850 ₽              │
│      Ресторан "Казан"                1 400 ₽              │
│      Ресторан "Тубатай"             1 100 ₽              │
│    Бронирования:                                          │
│      Авиабилет S7 (туда-обратно)    12 600 ₽              │
│    Суточные:                         3 587 ₽              │
│    = Итого факт                     36 737 ₽              │
│                                                            │
│  РЕЗУЛЬТАТ:                                                │
│    Аванс - Факт = 38 587 - 36 737 = +1 850 ₽             │
│    → Недоиспользование → возврат в бюджет компании        │
│                                                            │
│  Возможные исходы:                                        │
│    Δ > 0  → Недорасход → возврат в бюджет                 │
│    Δ = 0  → Точное соответствие                           │
│    Δ < 0  → Перерасход → запрос на возмещение сотруднику  │
│             или списание с зарплатной карты (с согласия)   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

#### Модель данных сверки

```sql
CREATE TABLE reconciliation_runs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID REFERENCES companies(id),
    trip_request_id     UUID REFERENCES trip_requests(id),

    run_type            VARCHAR(20) NOT NULL
                        CHECK (run_type IN ('DAILY', 'TRIP_CLOSURE', 'MANUAL')),

    total_transactions  INT NOT NULL DEFAULT 0,
    matched_count       INT NOT NULL DEFAULT 0,
    unmatched_count     INT NOT NULL DEFAULT 0,
    anomaly_count       INT NOT NULL DEFAULT 0,
    match_rate          DECIMAL(5,2),             -- %

    advance_amount      DECIMAL(15,2),            -- Для TRIP_CLOSURE
    actual_amount       DECIMAL(15,2),
    difference_amount   DECIMAL(15,2),
    difference_action   VARCHAR(20)
                        CHECK (difference_action IN (
                            'RETURN_TO_BUDGET', 'EMPLOYEE_REIMBURSEMENT',
                            'SALARY_DEDUCTION', 'WRITE_OFF', 'NONE'
                        )),

    status              VARCHAR(20) NOT NULL DEFAULT 'RUNNING'
                        CHECK (status IN (
                            'RUNNING', 'COMPLETED', 'FAILED',
                            'REQUIRES_REVIEW'
                        )),

    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at        TIMESTAMPTZ,
    reviewed_by         UUID REFERENCES employees(id),
    reviewed_at         TIMESTAMPTZ
);

CREATE TABLE reconciliation_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reconciliation_id   UUID NOT NULL REFERENCES reconciliation_runs(id),

    transaction_id      UUID REFERENCES card_transactions(id),
    booking_id          UUID REFERENCES bookings(id),
    payment_id          UUID REFERENCES payments(id),

    match_status        VARCHAR(20) NOT NULL
                        CHECK (match_status IN (
                            'MATCHED', 'UNMATCHED_TRANSACTION',
                            'UNMATCHED_BOOKING', 'AMOUNT_MISMATCH',
                            'DUPLICATE', 'SUSPICIOUS'
                        )),

    expected_amount     DECIMAL(15,2),
    actual_amount       DECIMAL(15,2),
    difference          DECIMAL(15,2),
    notes               TEXT,

    resolved            BOOLEAN DEFAULT false,
    resolved_by         UUID REFERENCES employees(id),
    resolved_at         TIMESTAMPTZ,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 9. Отчётность

### 9.1 Типы отчётов

| # | Отчёт | Периодичность | Получатель | Формат |
|---|-------|:-------------:|------------|--------|
| 1 | Финансовый отчёт по компании | Ежемесячно | CFO, бухгалтер | Excel, PDF |
| 2 | Расходы по подразделениям | Ежемесячно | CFO, руководители | Excel, PDF |
| 3 | Расходы по сотрудникам | Ежемесячно | CFO, HR | Excel |
| 4 | Бюджет vs. факт | Ежемесячно | CFO | Excel, Dashboard |
| 5 | Отчёт по кэшбэку | Ежемесячно | CFO | Excel |
| 6 | Отчёт по НДС | Ежеквартально | Бухгалтер | XML, Excel |
| 7 | Отчёт по суточным | Ежемесячно | Бухгалтер, HR | Excel |
| 8 | Авансовый отчёт | По командировке | Бухгалтер | Excel, 1С |
| 9 | Сверка с провайдерами | Ежедневно | Фин. контроль | Excel |
| 10 | Отчёт по экономии | Ежемесячно | CFO | PDF, Dashboard |

### 9.2 Структура ежемесячного финансового отчёта

```
╔══════════════════════════════════════════════════════════════════╗
║          ЕЖЕМЕСЯЧНЫЙ ФИНАНСОВЫЙ ОТЧЁТ                          ║
║          ООО "ТехноСервис" | Февраль 2026                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ОБЩИЕ ПОКАЗАТЕЛИ                                               ║
║  ────────────────                                               ║
║  Количество командировок:              47                       ║
║  Количество сотрудников:               32                       ║
║  Общий бюджет:                  2 150 000 ₽                     ║
║  Фактические расходы:           1 876 430 ₽                     ║
║  Экономия:                        273 570 ₽ (12.7%)            ║
║                                                                  ║
║  РАСХОДЫ ПО КАТЕГОРИЯМ                                         ║
║  ──────────────────────                                         ║
║  ┌────────────────────┬────────────┬─────────┬───────────┐      ║
║  │ Категория          │ Сумма      │ Доля    │ vs прогноз│      ║
║  ├────────────────────┼────────────┼─────────┼───────────┤      ║
║  │ Авиабилеты         │   987 230 ₽│  52.6%  │  -3.2%    │      ║
║  │ Проживание         │   512 400 ₽│  27.3%  │  +1.1%    │      ║
║  │ Ж/д билеты         │   156 800 ₽│   8.4%  │  -5.7%    │      ║
║  │ Такси              │    89 200 ₽│   4.8%  │  +2.3%    │      ║
║  │ Питание            │    78 500 ₽│   4.2%  │  -0.8%    │      ║
║  │ Прочее             │    52 300 ₽│   2.8%  │  +0.5%    │      ║
║  └────────────────────┴────────────┴─────────┴───────────┘      ║
║                                                                  ║
║  КЭШБЭК                                                        ║
║  ───────                                                        ║
║  Начислено за период:               87 450 ₽                   ║
║  Зачислено на корп. счёт:           65 200 ₽                   ║
║  Бонусы сотрудникам:                22 250 ₽                   ║
║                                                                  ║
║  НДС                                                            ║
║  ───                                                            ║
║  НДС к возмещению:                 103 860 ₽                   ║
║  Документы собраны:                     94%                     ║
║  Ожидают подписания:                     6%                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 9.3 Форматы экспорта

| Формат | Назначение | Технология |
|--------|------------|------------|
| Excel (.xlsx) | Бухгалтерия, анализ | Apache POI / openpyxl |
| PDF | Руководство, печать | wkhtmltopdf / Puppeteer |
| CSV | Интеграции, 1С | Стандартный вывод |
| XML | Налоговая отчётность | JAXB / lxml |
| JSON (API) | Интеграции, дашборды | REST API |

---

## 10. API Reference

### 10.1 Виртуальные карты

#### POST /api/v1/cards — Выпуск виртуальной карты

**Запрос:**

```json
{
  "trip_request_id": "tr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "employee_id": "emp_98765432-dcba-0987-6543-210fedcba098",
  "limit_amount": 35000.00,
  "currency": "RUB",
  "category_restrictions": ["transport", "accommodation", "meals", "taxi"],
  "auto_activate_on_trip_start": true
}
```

**Ответ (201 Created):**

```json
{
  "id": "vc_f1e2d3c4-b5a6-9870-1234-567890abcdef",
  "card_id": "tbc_internal_001234",
  "trip_request_id": "tr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "employee_id": "emp_98765432-dcba-0987-6543-210fedcba098",
  "status": "ISSUED",
  "card_number_masked": "****4521",
  "limit_amount": 35000.00,
  "spent_amount": 0.00,
  "remaining_amount": 35000.00,
  "currency": "RUB",
  "category_restrictions": ["transport", "accommodation", "meals", "taxi"],
  "issued_at": "2026-03-01T10:15:30Z",
  "activated_at": null,
  "expires_at": "2026-03-15T23:59:59Z"
}
```

#### GET /api/v1/cards/:id — Детали карты

**Ответ (200 OK):**

```json
{
  "id": "vc_f1e2d3c4-b5a6-9870-1234-567890abcdef",
  "card_id": "tbc_internal_001234",
  "status": "ACTIVE",
  "card_number_masked": "****4521",
  "limit_amount": 35000.00,
  "spent_amount": 18450.00,
  "remaining_amount": 16550.00,
  "currency": "RUB",
  "category_restrictions": ["transport", "accommodation", "meals", "taxi"],
  "recent_transactions": [
    {
      "id": "tx_001",
      "amount": 15200.00,
      "merchant_name": "Holiday Inn Kazan",
      "expense_category": "ACCOMMODATION",
      "status": "SETTLED",
      "transaction_at": "2026-03-10T14:22:00Z"
    },
    {
      "id": "tx_002",
      "amount": 1850.00,
      "merchant_name": "Яндекс.Такси",
      "expense_category": "TAXI",
      "status": "SETTLED",
      "transaction_at": "2026-03-10T09:15:00Z"
    }
  ],
  "issued_at": "2026-03-01T10:15:30Z",
  "activated_at": "2026-03-10T00:00:00Z"
}
```

#### PATCH /api/v1/cards/:id/block — Блокировка карты

**Запрос:**

```json
{
  "reason": "TRIP_ENDED",
  "comment": "Командировка завершена 14.03.2026"
}
```

**Ответ (200 OK):**

```json
{
  "id": "vc_f1e2d3c4-b5a6-9870-1234-567890abcdef",
  "status": "BLOCKED",
  "blocked_at": "2026-03-15T00:00:00Z",
  "blocked_reason": "TRIP_ENDED"
}
```

#### GET /api/v1/cards/:id/transactions — Транзакции по карте

**Query parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `status` | string | Фильтр: PENDING, SETTLED, REVERSED, DISPUTED |
| `category` | string | Фильтр: TRANSPORT, ACCOMMODATION, MEALS, TAXI, OTHER |
| `from_date` | ISO 8601 | Начало периода |
| `to_date` | ISO 8601 | Конец периода |
| `page` | int | Номер страницы (default: 1) |
| `per_page` | int | Записей на странице (default: 50, max: 200) |

**Ответ (200 OK):**

```json
{
  "data": [
    {
      "id": "tx_a1b2c3d4",
      "card_id": "vc_f1e2d3c4-b5a6-9870-1234-567890abcdef",
      "trip_request_id": "tr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "amount": 15200.00,
      "currency": "RUB",
      "merchant_name": "Holiday Inn Kazan City Centre",
      "merchant_city": "Казань",
      "merchant_country": "RUS",
      "merchant_category_code": "7011",
      "expense_category": "ACCOMMODATION",
      "description": "Проживание 10-13.03.2026, 3 ночи",
      "receipt_url": "https://storage.t-komandirovka.ru/receipts/rx_001.pdf",
      "receipt_status": "OCR_DONE",
      "status": "SETTLED",
      "authorization_code": "A12345",
      "transaction_at": "2026-03-10T14:22:00Z",
      "settled_at": "2026-03-12T03:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_count": 5,
    "total_pages": 1
  }
}
```

### 10.2 Платежи

#### POST /api/v1/payments/initiate — Инициация платежа

**Запрос:**

```json
{
  "company_id": "comp_xyz789",
  "trip_request_id": "tr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "booking_id": "bk_001234",
  "payment_method": "CORPORATE_ACCOUNT",
  "amount": 12600.00,
  "currency": "RUB",
  "is_deferred": false,
  "description": "Авиабилет S7 Airlines MOW-KZN-MOW"
}
```

**Ответ (201 Created):**

```json
{
  "id": "pay_98765432",
  "status": "HOLD",
  "amount": 12600.00,
  "currency": "RUB",
  "payment_method": "CORPORATE_ACCOUNT",
  "hold_at": "2026-03-01T10:20:00Z",
  "description": "Авиабилет S7 Airlines MOW-KZN-MOW",
  "is_deferred": false,
  "due_date": null
}
```

#### GET /api/v1/payments/:id — Статус платежа

**Ответ (200 OK):**

```json
{
  "id": "pay_98765432",
  "company_id": "comp_xyz789",
  "trip_request_id": "tr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "booking_id": "bk_001234",
  "status": "SETTLED",
  "amount": 12600.00,
  "currency": "RUB",
  "vat_amount": 0.00,
  "vat_rate": 0.00,
  "payment_method": "CORPORATE_ACCOUNT",
  "provider_name": "S7 Airlines",
  "provider_reference": "S7-2026-0301-4521",
  "hold_at": "2026-03-01T10:20:00Z",
  "settled_at": "2026-03-01T10:25:30Z",
  "is_deferred": false
}
```

### 10.3 Суточные

#### POST /api/v1/per-diem/calculate — Расчёт суточных

**Запрос:**

```json
{
  "company_id": "comp_xyz789",
  "employee_id": "emp_98765432",
  "trip_request_id": "tr_a1b2c3d4",
  "destination_city": "Казань",
  "destination_country": "RUS",
  "start_date": "2026-03-10",
  "end_date": "2026-03-14"
}
```

**Ответ (200 OK):**

```json
{
  "id": "pd_calc_001",
  "trip_request_id": "tr_a1b2c3d4",
  "destination_city": "Казань",
  "destination_country": "RUS",
  "city_tier": "TIER_2",
  "start_date": "2026-03-10",
  "end_date": "2026-03-14",
  "total_days": 5,
  "daily_rate": 900.00,
  "breakdown": [
    {"date": "2026-03-10", "type": "arrival", "factor": 0.5, "amount": 450.00},
    {"date": "2026-03-11", "type": "full", "factor": 1.0, "amount": 900.00},
    {"date": "2026-03-12", "type": "full", "factor": 1.0, "amount": 900.00},
    {"date": "2026-03-13", "type": "full", "factor": 1.0, "amount": 900.00},
    {"date": "2026-03-14", "type": "departure", "factor": 0.5, "amount": 450.00}
  ],
  "gross_amount": 3600.00,
  "tax_threshold_daily": 700.00,
  "tax_free_amount": 3500.00,
  "taxable_amount": 100.00,
  "ndfl_amount": 13.00,
  "insurance_amount": 30.00,
  "net_amount": 3587.00,
  "payment_status": "PENDING",
  "scheduled_payment_date": "2026-03-09"
}
```

### 10.4 Кэшбэк

#### GET /api/v1/cashback/summary — Сводка по кэшбэку

**Query parameters:** `company_id`, `from_date`, `to_date`

**Ответ (200 OK):**

```json
{
  "company_id": "comp_xyz789",
  "period": {
    "from": "2026-02-01",
    "to": "2026-02-28"
  },
  "summary": {
    "total_booking_amount": 1876430.00,
    "total_cashback_accrued": 87450.00,
    "total_cashback_confirmed": 65200.00,
    "total_cashback_pending": 22250.00,
    "effective_cashback_rate": 4.66
  },
  "by_category": [
    {"category": "FLIGHT", "booking_amount": 987230.00, "cashback": 49361.50, "rate": 5.0},
    {"category": "HOTEL", "booking_amount": 512400.00, "cashback": 25620.00, "rate": 5.0},
    {"category": "TRAIN", "booking_amount": 156800.00, "cashback": 7840.00, "rate": 5.0},
    {"category": "TAXI", "booking_amount": 89200.00, "cashback": 2676.00, "rate": 3.0},
    {"category": "OTHER", "booking_amount": 130800.00, "cashback": 1952.50, "rate": 1.5}
  ],
  "employee_bonuses": {
    "total_savings_generated": 273570.00,
    "company_share": 191499.00,
    "employee_bonuses_total": 82071.00,
    "top_savers": [
      {"employee_id": "emp_001", "name": "Иванов И.И.", "savings": 45200.00, "bonus": 13560.00},
      {"employee_id": "emp_002", "name": "Петров П.П.", "savings": 38100.00, "bonus": 11430.00},
      {"employee_id": "emp_003", "name": "Сидорова А.В.", "savings": 31800.00, "bonus": 9540.00}
    ]
  }
}
```

### 10.5 Закрывающие документы

#### POST /api/v1/documents/generate — Генерация документа

**Запрос:**

```json
{
  "company_id": "comp_xyz789",
  "document_type": "UPD",
  "trip_request_id": "tr_a1b2c3d4",
  "booking_ids": ["bk_001234", "bk_001235"],
  "format": "PDF",
  "send_via_edo": true,
  "edo_provider": "DIADOK"
}
```

**Ответ (201 Created):**

```json
{
  "id": "doc_abc123",
  "document_type": "UPD",
  "document_number": "УПД-2026-03-00147",
  "document_date": "2026-03-15",
  "amount_with_vat": 15200.00,
  "amount_without_vat": 12666.67,
  "vat_amount": 2533.33,
  "vat_rate": 20.00,
  "file_url": "https://storage.t-komandirovka.ru/docs/doc_abc123.pdf",
  "signature_status": "SIGNED_BY_ISSUER",
  "edo_status": "SENT",
  "edo_document_id": "diadok_ext_98765"
}
```

#### GET /api/v1/documents — Список документов

**Query parameters:** `company_id`, `document_type`, `from_date`, `to_date`, `status`, `page`, `per_page`

**Ответ (200 OK):**

```json
{
  "data": [
    {
      "id": "doc_abc123",
      "document_type": "UPD",
      "document_number": "УПД-2026-03-00147",
      "document_date": "2026-03-15",
      "amount_with_vat": 15200.00,
      "vat_amount": 2533.33,
      "recipient_name": "ООО \"ТехноСервис\"",
      "signature_status": "SIGNED_BY_BOTH",
      "edo_status": "ACCEPTED"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_count": 147,
    "total_pages": 3
  }
}
```

### 10.6 Сверка

#### POST /api/v1/reconciliation/run — Запуск сверки

**Запрос:**

```json
{
  "run_type": "TRIP_CLOSURE",
  "trip_request_id": "tr_a1b2c3d4",
  "company_id": "comp_xyz789"
}
```

**Ответ (202 Accepted):**

```json
{
  "id": "recon_001",
  "run_type": "TRIP_CLOSURE",
  "status": "RUNNING",
  "started_at": "2026-03-15T10:00:00Z",
  "estimated_completion": "2026-03-15T10:01:00Z"
}
```

**Ответ после завершения (GET /api/v1/reconciliation/:id):**

```json
{
  "id": "recon_001",
  "run_type": "TRIP_CLOSURE",
  "status": "COMPLETED",
  "trip_request_id": "tr_a1b2c3d4",
  "results": {
    "total_transactions": 5,
    "matched_count": 5,
    "unmatched_count": 0,
    "anomaly_count": 0,
    "match_rate": 100.00,
    "advance_amount": 38587.00,
    "actual_amount": 36737.00,
    "difference_amount": 1850.00,
    "difference_action": "RETURN_TO_BUDGET"
  },
  "items": [
    {
      "transaction_id": "tx_001",
      "booking_id": "bk_001234",
      "match_status": "MATCHED",
      "expected_amount": 12600.00,
      "actual_amount": 12600.00,
      "difference": 0.00
    }
  ],
  "started_at": "2026-03-15T10:00:00Z",
  "completed_at": "2026-03-15T10:00:45Z"
}
```

### 10.7 Сводная таблица эндпоинтов

| Метод | Путь | Описание | Auth |
|-------|------|----------|:----:|
| `POST` | `/api/v1/cards` | Выпуск виртуальной карты | Bearer |
| `GET` | `/api/v1/cards/:id` | Детали карты | Bearer |
| `PATCH` | `/api/v1/cards/:id/block` | Блокировка карты | Bearer |
| `PATCH` | `/api/v1/cards/:id/unblock` | Разблокировка карты | Bearer |
| `GET` | `/api/v1/cards/:id/transactions` | Транзакции по карте | Bearer |
| `POST` | `/api/v1/payments/initiate` | Инициация платежа | Bearer |
| `GET` | `/api/v1/payments/:id` | Статус платежа | Bearer |
| `POST` | `/api/v1/payments/:id/refund` | Возврат платежа | Bearer |
| `POST` | `/api/v1/per-diem/calculate` | Расчёт суточных | Bearer |
| `POST` | `/api/v1/per-diem/:id/credit` | Зачисление суточных | Bearer |
| `GET` | `/api/v1/cashback/summary` | Сводка по кэшбэку | Bearer |
| `GET` | `/api/v1/cashback/transactions` | Транзакции кэшбэка | Bearer |
| `POST` | `/api/v1/documents/generate` | Генерация документа | Bearer |
| `GET` | `/api/v1/documents` | Список документов | Bearer |
| `GET` | `/api/v1/documents/:id` | Детали документа | Bearer |
| `GET` | `/api/v1/documents/:id/download` | Скачивание документа | Bearer |
| `POST` | `/api/v1/reconciliation/run` | Запуск сверки | Bearer |
| `GET` | `/api/v1/reconciliation/:id` | Результат сверки | Bearer |
| `GET` | `/api/v1/reports/monthly` | Ежемесячный отчёт | Bearer |
| `GET` | `/api/v1/reports/vat` | Отчёт по НДС | Bearer |
| `GET` | `/api/v1/credit-lines/:company_id` | Кредитная линия | Bearer |

---

## 11. Безопасность

### 11.1 PCI DSS Compliance

Модуль обрабатывает данные банковских карт и обязан соответствовать стандарту PCI DSS Level 1.

```
┌──────────────────────────────────────────────────────────────────┐
│                    PCI DSS ТРЕБОВАНИЯ                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Требование 1: Сетевая защита                                   │
│  ├── WAF перед всеми публичными эндпоинтами                     │
│  ├── Сегментация сети: CDE (Cardholder Data Environment)        │
│  └── Firewall rules: whitelist-only                             │
│                                                                  │
│  Требование 3: Защита хранимых данных                           │
│  ├── PAN хранится ТОЛЬКО в T-Bank Processing (не у нас)         │
│  ├── В нашей БД — только masked PAN (****4521)                  │
│  ├── CVV не хранится НИКОГДА                                    │
│  └── Шифрование: AES-256 для всех чувствительных полей          │
│                                                                  │
│  Требование 4: Шифрование передачи                              │
│  ├── TLS 1.3 для всех API                                      │
│  ├── mTLS для internal API (к T-Bank Card Processing)           │
│  └── Certificate pinning для mobile                             │
│                                                                  │
│  Требование 7: Ограничение доступа                              │
│  ├── RBAC: card data доступны только authorized roles            │
│  ├── Audit log всех обращений к card data                       │
│  └── Принцип наименьших привилегий                              │
│                                                                  │
│  Требование 10: Мониторинг и логирование                        │
│  ├── Все доступы к card data логируются                         │
│  ├── Log retention: 1 год онлайн, 5 лет в архиве               │
│  └── SIEM интеграция (Splunk / ELK)                            │
│                                                                  │
│  Требование 12: Политики безопасности                           │
│  ├── Ежеквартальное сканирование ASV                            │
│  ├── Ежегодный аудит QSA                                       │
│  └── Incident response plan                                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 11.2 Маскирование данных карт

| Контекст | Отображение PAN | Пример |
|----------|:---------------:|--------|
| UI (все пользователи) | Маскированный | ****4521 |
| API response | Маскированный | ****4521 |
| Логи приложения | Маскированный | ****4521 |
| База данных | Маскированный | ****4521 |
| Уведомления (push/email) | Маскированный | ****4521 |
| T-Bank Processing (internal) | Полный PAN | 5536 9100 1234 4521 |

### 11.3 Подписание транзакций

Каждая финансовая операция подписывается для обеспечения целостности и неотказуемости:

```
Transaction payload
        │
        ▼
┌───────────────────┐
│  Canonical form    │  JSON → sorted keys → minified
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  HMAC-SHA256      │  key = per-company signing key
│  (payload)        │  → signature
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Store:           │
│  transaction_id   │
│  signature        │
│  signed_at        │
│  signer_key_id    │
└───────────────────┘
```

### 11.4 Двойная авторизация крупных платежей

| Сумма | Уровень авторизации |
|------:|---------------------|
| < 100 000 ₽ | Автоматически (policy check) |
| 100 000 — 500 000 ₽ | Одобрение руководителя подразделения |
| 500 000 — 1 000 000 ₽ | Руководитель подразделения + CFO |
| > 1 000 000 ₽ | CFO + CEO (или совет директоров) |

### 11.5 Обнаружение мошенничества (Fraud Detection)

| # | Правило | Действие | Порог |
|---|---------|----------|-------|
| 1 | Транзакция в нерабочее время (00:00–06:00) | Alert | Уведомление |
| 2 | Транзакция в городе, отличном от пункта назначения | Alert + Review | Уведомление |
| 3 | Множественные транзакции < 5 мин (> 3) | Block | Автоблокировка |
| 4 | Транзакция превышает 50% лимита карты | Alert | Уведомление |
| 5 | MCC: алкоголь, развлечения (если в blacklist) | Decline | Автоотклонение |
| 6 | Транзакция после даты окончания командировки | Block | Автоблокировка |
| 7 | Дублирование суммы + merchant за < 1 час | Alert | Уведомление |
| 8 | Географическая аномалия (2 города за < 2 часа) | Block | Автоблокировка |

---

## 12. Метрики

### 12.1 SLA и целевые показатели

| # | Метрика | Целевое значение | Способ измерения |
|---|---------|:----------------:|------------------|
| 1 | Время выпуска виртуальной карты | < 5 секунд | P95 от запроса до ISSUED |
| 2 | Время обработки авторизации MCC | < 100 мс | P99 от webhook до ответа |
| 3 | Время обработки транзакции (settlement) | < 3 секунд | P95 от webhook до записи в БД |
| 4 | Точность начисления кэшбэка | 99.99% | Ошибки / общее количество |
| 5 | Процент успешного возмещения НДС | > 95% | Возмещённый / начисленный НДС |
| 6 | Match rate ежедневной сверки | > 98% | Matched / total транзакций |
| 7 | Время генерации закрывающего документа | < 10 секунд | P95 от запроса до файла |
| 8 | Доступность платёжных API | 99.95% | Uptime за месяц |
| 9 | Время зачисления суточных | < 1 часа | От одобрения поездки до зачисления |
| 10 | Время закрытия командировки (reconciliation) | < 1 рабочего дня | P90 от trip_end до CLOSED |

### 12.2 Бизнес-метрики

| Метрика | Описание | Целевое значение (Year 1) |
|---------|----------|:-------------------------:|
| Средний кэшбэк на компанию | Ежемесячный кэшбэк | > 50 000 ₽ |
| Экономия бюджета клиента | Снижение расходов благодаря платформе | 20-30% |
| Доля автоматических согласований | Транзакции без ручного вмешательства | > 80% |
| Adoption rate виртуальных карт | Компании, использующие карты | > 60% |
| NPS по финансовому модулю | Удовлетворённость бухгалтеров | > 50 |
| Время на авансовый отчёт | Снижение затрат времени | С 4-6ч до < 15 мин |
| Доля ЭДО-документов | Документы, отправленные через ЭДО | > 70% |

### 12.3 Дашборд мониторинга

```
╔══════════════════════════════════════════════════════════════════╗
║              FINANCE MODULE — OPERATIONS DASHBOARD              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  КАРТЫ                          ПЛАТЕЖИ                         ║
║  ──────                         ───────                         ║
║  Активных:    1 247             Сегодня:         3 891          ║
║  Выпущено сегодня: 34           GMV:       12.4M ₽              ║
║  Заблокировано:    12           Успех:       99.7%              ║
║  Ср. время выпуска: 3.2s       Отсрочка:    1.8M ₽             ║
║                                                                  ║
║  ТРАНЗАКЦИИ                     КЭШБЭК                         ║
║  ──────────                     ──────                          ║
║  Сегодня:    2 156              Начислено сегодня: 547K ₽       ║
║  Approved:   2 089 (96.9%)      Зачислено:         312K ₽      ║
║  Declined:      67 (3.1%)       Pending:           235K ₽      ║
║  Fraud alerts:   3              Ставка:            4.4%         ║
║                                                                  ║
║  СВЕРКА                         НДС                             ║
║  ──────                         ───                             ║
║  Match rate:   98.7%            К возмещению:   2.1M ₽          ║
║  Unmatched:       28            Документов:        94%          ║
║  Anomalies:        4            На проверке:         6%         ║
║  Last run:   02:15 MSK          Отклонено:           0%         ║
║                                                                  ║
║  ┌──────────────────────────────────────────────────────────┐   ║
║  │  ALERTS                                                  │   ║
║  │  🔴 3 fraud alerts require review                        │   ║
║  │  🟡 28 unmatched transactions from daily recon           │   ║
║  │  🟢 All systems operational                              │   ║
║  └──────────────────────────────────────────────────────────┘   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Приложение A. Глоссарий

| Термин | Описание |
|--------|----------|
| **MCC** | Merchant Category Code — 4-значный код категории торговой точки |
| **PAN** | Primary Account Number — полный номер карты |
| **BIN** | Bank Identification Number — первые 6-8 цифр карты |
| **CVV** | Card Verification Value — код безопасности на обороте карты |
| **PCI DSS** | Payment Card Industry Data Security Standard |
| **ЭДО** | Электронный документооборот |
| **КЭДО** | Кадровый электронный документооборот |
| **УПД** | Универсальный передаточный документ |
| **НДС** | Налог на добавленную стоимость |
| **НДФЛ** | Налог на доходы физических лиц |
| **КЭП** | Квалифицированная электронная подпись |
| **УКЭП** | Усиленная квалифицированная электронная подпись |
| **CDE** | Cardholder Data Environment — среда обработки данных карт |
| **ASV** | Approved Scanning Vendor — сертифицированный поставщик сканирования |
| **QSA** | Qualified Security Assessor — аудитор PCI DSS |
| **WAF** | Web Application Firewall |
| **mTLS** | Mutual TLS — двусторонняя аутентификация по сертификатам |
| **SIEM** | Security Information and Event Management |

## Приложение B. Связи с другими модулями

```
┌──────────────────────────────────────────────────────────────────┐
│                     МЕЖМОДУЛЬНЫЕ СВЯЗИ                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SPEC-01: AI-агент                                              │
│  ├── Получает: информацию о доступном бюджете                   │
│  ├── Отправляет: запрос на выпуск карты при бронировании        │
│  └── Отправляет: запрос на расчёт суточных                     │
│                                                                  │
│  SPEC-02: Бронирование                                         │
│  ├── Получает: подтверждение оплаты                             │
│  ├── Отправляет: booking_confirmed → начисление кэшбэка         │
│  └── Отправляет: booking_cancelled → reversal кэшбэка           │
│                                                                  │
│  SPEC-03: Управление (заявки, согласование)                     │
│  ├── Получает: статус оплаты для отображения                    │
│  ├── Отправляет: trip_approved → выпуск карты + суточные        │
│  └── Отправляет: trip_cancelled → закрытие карты + отмена       │
│                                                                  │
│  SPEC-05: Отчётность и аналитика                               │
│  ├── Получает: финансовые данные для дашбордов                  │
│  ├── Получает: данные сверки для отчётов                        │
│  └── Получает: экспорт данных (Excel, CSV, 1С)                 │
│                                                                  │
│  SPEC-06: Интеграции (1С, ЭДО)                                 │
│  ├── Получает: закрывающие документы для ЭДО                    │
│  ├── Получает: записи книги покупок (НДС)                      │
│  └── Отправляет: подтверждение доставки документов              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Приложение C. Changelog

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 01.03.2026 | Первая версия спецификации |

---

*Конфиденциально. Т-Командировка © 2026. Все права защищены.*

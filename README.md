# 📊 Stock Market Bot

Telegram-бот для анализа рынка акций на Python.

Анализирует российские и американские акции: исторические данные, технические индикаторы, новости и AI-аналитику.

---

## ✨ Возможности

- 📈 Исторические данные цены за 1 год
- 📐 Технические индикаторы: SMA20, SMA50, RSI(14)
- ⚡ Волатильность и изменение цены за 7/30/180 дней
- 📊 Красивый график с тёмной темой
- 📰 Последние новости через NewsAPI
- 🤖 AI-анализ через OpenAI (опционально)
- 🔍 Rule-based анализ (работает без API-ключей)
- 🇷🇺 Российские акции через MOEX ISS API (данные Московской биржи)
- 🇺🇸 Американские акции через yfinance

---

## 🏦 Источники данных

| Тип тикера | Источник | Пример |
|---|---|---|
| Американские акции | yfinance | `AAPL`, `TSLA`, `NVDA` |
| Российские акции (`*.ME`) | yfinance → fallback MOEX ISS | `SBER.ME`, `GAZP.ME` |
| Российские (короткий тикер) | MOEX ISS | `SBER`, `GAZP`, `LKOH` |
| Русское название | MOEX ISS | `сбербанк`, `яндекс` |

Для российских акций бот сначала пробует yfinance; если данные недоступны — автоматически использует публичный [MOEX ISS API](https://iss.moex.com/) (не требует ключей).

---

## 🚀 Быстрый старт

### 1. Создание бота через BotFather

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Придумайте имя и username для бота
4. Скопируйте токен вида `123456789:ABCdefGhI...`

### 2. Установка зависимостей

```bash
# Клонируйте или распакуйте проект
cd stock_market_bot

# Создайте виртуальное окружение (рекомендуется)
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# Установите зависимости
pip install -r requirements.txt
```

### 3. Настройка .env

```bash
cp .env.example .env
```

Откройте `.env` и заполните:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhI...   # обязательно
NEWS_API_KEY=                                # необязательно
OPENAI_API_KEY=                              # необязательно
```

### 4. Запуск

```bash
python run.py
```

Бот запустится и начнёт принимать сообщения. Найдите вашего бота в Telegram и отправьте `/start`.

---

## 📱 Способы использования

### ✍️ Просто написать (самый простой способ)

Отправьте любое из следующего прямо в чат — бот сам поймёт:

```
Сбербанк          — анализ Сбербанка
Газпром           — анализ Газпрома
Apple             — анализ Apple
Tesla             — анализ Tesla
Nvidia            — анализ Nvidia
SBER              — по короткому тикеру MOEX
SBER.ME           — по полному тикеру MOEX
AAPL              — по тикеру NYSE
TSLA              — по тикеру NASDAQ
MSFT
```

### 📌 Команда /analyze

```
/analyze AAPL
/analyze SBER
/analyze SBER.ME
/analyze сбербанк
/analyze tesla
/analyze spacex   — объяснит, что SpaceX частная компания
```

### 🔘 Кнопки в меню

После `/start` появляются кнопки быстрого выбора: Сбербанк, Газпром, Apple, Tesla, Nvidia, Microsoft.

---

## 📰 Как включить новости (NewsAPI)

1. Зарегистрируйтесь на [newsapi.org](https://newsapi.org/register) — бесплатно
2. Получите API-ключ в личном кабинете
3. Добавьте в `.env`:
   ```env
   NEWS_API_KEY=ваш_ключ_здесь
   ```

Бесплатный план позволяет 100 запросов в день.

---

## 🤖 Как включить AI-анализ (OpenAI)

1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
2. Создайте API-ключ в разделе API Keys
3. Добавьте в `.env`:
   ```env
   OPENAI_API_KEY=sk-...ваш_ключ...
   ```

Если ключ не указан — бот использует встроенный rule-based анализ.

---

## 🧪 Запуск тестов

```bash
pytest tests/ -v
```

Или отдельные модули:
```bash
pytest tests/test_ticker_resolver.py -v
pytest tests/test_analysis_service.py -v
pytest tests/test_moex_data.py -v
```

---

## 🗂 Структура проекта

```
stock_market_bot/
├── run.py                      # точка входа
├── requirements.txt
├── .env.example
├── README.md
├── bot/
│   ├── __init__.py
│   ├── main.py                 # сборка приложения, запуск polling
│   ├── handlers.py             # обработчики команд и callback
│   └── keyboards.py            # inline-клавиатуры
├── services/
│   ├── __init__.py
│   ├── ticker_resolver.py      # перевод названия компании → тикер
│   ├── market_data.py          # yfinance + MOEX ISS fallback
│   ├── moex_data.py            # клиент MOEX ISS API
│   ├── chart_service.py        # генерация графика (matplotlib)
│   ├── news_service.py         # новости через NewsAPI
│   └── analysis_service.py     # rule-based и AI анализ
├── utils/
│   ├── __init__.py
│   ├── config.py               # переменные окружения
│   └── formatters.py           # форматирование сообщений
└── tests/
    ├── __init__.py
    ├── test_ticker_resolver.py
    ├── test_analysis_service.py
    └── test_moex_data.py
```

---

## 🛡 Дисклеймер

Бот предоставляет аналитический обзор на основе доступных данных.
**Это не инвестиционная рекомендация.** Все инвестиционные решения вы принимаете самостоятельно.

---

## 📄 Лицензия

MIT License

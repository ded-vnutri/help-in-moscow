# Help in Moscow

Telegram-бот для иностранцев в Москве: студентов, туристов и новых жителей. Отвечает на вопросы на 9 языках, ищет свежую информацию в интернете и находит ближайшие аптеки, метро, салоны связи, банкоматы и больницы по геолокации.

## Что умеет

- `/start` и `/chooselanguage`: выбор языка (English, Русский, 中文, العربية, Français, Español, हिन्दी, فارسی, Türkçe).
- Кнопки с темами: SIM-карта, транспорт, документы, медицина, деньги и банки, учёба, жильё, такси, экстренная помощь. Ответ всегда на выбранном языке.
- Любой вопрос своими словами или голосовым сообщением. Бот ищет свежие страницы в интернете (бесплатно через DuckDuckGo или платно через OpenRouter), передаёт их нейросети и помнит последние 3 вопроса.
- Ответы в одном стиле: эмодзи и заголовок, 3–5 пунктов, совет, ссылка. Под каждым ответом кнопки 👍/👎.
- `/stats` для админа (ADMIN_ID): пользователи, вопросы, языки, оценки и последние вопросы с 👎.
- «📍 Рядом со мной»: человек отправляет геолокацию, выбирает, что ищет, и получает 5 ближайших мест со ссылкой на пеший маршрут в Яндекс Картах. Данные берутся из OpenStreetMap бесплатно.
- Лимиты на запросы к нейросети: по умолчанию 30 в день на человека и 300 в день на всех.

## Что нужно перед запуском

1. **Токен бота.** Напиши [@BotFather](https://t.me/BotFather), отправь `/newbot`, придумай имя и username. Он пришлёт токен вида `123456:ABC...`.
2. **Ключ OpenRouter.** Зарегистрируйся на [openrouter.ai](https://openrouter.ai), пополни баланс на 5 $ (Credits) и создай ключ в разделе [Keys](https://openrouter.ai/keys).
3. Скопируй `.env.example` в `.env` и впиши туда токен и ключ. Файл `.env` никому не отправляй и не заливай на GitHub (он уже в `.gitignore`).

## Запуск на своём компьютере (для проверки)

Нужен Python 3.11 или новее.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
pip install -r requirements-voice.txt   # необязательно: голосовые сообщения
python -m bot
```

Если в консоли появилось `Help in Moscow bot started`, напиши боту `/start` в Telegram.

## Запуск на сервере с Proxmox

Проще всего сделать отдельный LXC-контейнер с Debian 12 и Docker.

1. В Proxmox: **Create CT**, шаблон Debian 12, 1 ядро, 512 МБ памяти, 4 ГБ диска. В разделе **Options → Features** включи `nesting` (нужно для Docker).
2. Зайди в консоль контейнера и поставь Docker и git:
   ```bash
   apt update && apt install -y git curl
   curl -fsSL https://get.docker.com | sh
   ```
3. Скачай код и заполни `.env`:
   ```bash
   git clone https://github.com/<твой-логин>/help-in-moscow.git
   cd help-in-moscow
   cp .env.example .env
   nano .env
   ```
4. Запусти:
   ```bash
   docker compose up -d --build
   docker compose logs -f     # посмотреть логи, выход Ctrl+C
   ```

Бот перезапускается сам после перезагрузки сервера. Обновить после изменений в коде: `git pull && docker compose up -d --build`.

## Если Telegram или OpenRouter не открываются с сервера

Если сервер в России, Telegram API иногда замедляют, а часть зарубежных сервисов может не открываться. Тогда впиши в `.env` прокси, например `PROXY_URL=socks5://user:pass@host:1080`. Он используется и для Telegram, и для OpenRouter, и для карт.

## Сколько это стоит

- Сама модель DeepSeek стоит доли цента за ответ.
- Основной расход идёт на поиск в интернете: на OpenRouter это примерно 4 $ за 1000 найденных страниц, то есть около 1,2 цента за вопрос при `WEB_MAX_RESULTS=3`. Цифры примерные, актуальные цены смотри на странице модели на OpenRouter.
- Ответы по кнопкам тем кешируются на 6 часов и повторно не оплачиваются.
- Если нужно экономить, поставь `WEB_MAX_RESULTS=1` или `WEB_SEARCH=false`: тогда бот ищет бесплатно через DuckDuckGo (`FREE_SEARCH=true`).

## Настройки в `.env`

| Параметр | Что значит | По умолчанию |
| --- | --- | --- |
| `BOT_TOKEN` | Токен от BotFather | обязательно |
| `OPENROUTER_API_KEY` | Ключ OpenRouter | обязательно |
| `OPENROUTER_MODEL` | Модель на OpenRouter | `deepseek/deepseek-v4-flash` |
| `REASONING` | Скрытые рассуждения модели | `false` |
| `WEB_SEARCH` | Платный поиск OpenRouter перед ответом | `false` |
| `FREE_SEARCH` | Бесплатный поиск DuckDuckGo, если платный выключен | `true` |
| `VOICE` / `WHISPER_MODEL` | Голосовые сообщения и размер модели | `true` / `base` |
| `ADMIN_ID` | Кому доступна /stats | пусто |
| `OPENROUTER_FALLBACK_MODEL` | Запасная модель | пусто |
| `WEB_MAX_RESULTS` | Сколько страниц брать из поиска | `3` |
| `USER_DAILY_LIMIT` | Вопросов в день на одного человека | `30` |
| `GLOBAL_DAILY_LIMIT` | Вопросов в день на всех | `300` |
| `PROXY_URL` | Прокси для доступа к Telegram и OpenRouter | пусто |
| `DB_PATH` | Где хранить базу пользователей | `data/bot.db` |

## Структура

```
bot/
  __main__.py   запуск бота
  config.py     настройки из .env
  handlers.py   команды, кнопки, сообщения
  i18n.py       тексты интерфейса на 9 языках и темы
  llm.py        запросы к OpenRouter
  geo.py        поиск мест рядом через OpenStreetMap
  search.py     бесплатный поиск в интернете (DuckDuckGo)
  voice.py      распознавание голосовых (faster-whisper)
  db.py         SQLite: язык, геолокация, счётчики запросов
  net.py        HTTP-сессии с прокси
```

## Что можно добавить потом

- Оплату: 3 бесплатных запроса, дальше подписка.
- Новые темы в меню (они задаются в `bot/i18n.py`).

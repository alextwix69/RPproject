# Гайд по архитектуре Telegram-бота RoleHub

Этот документ помогает быстро разобраться, как устроен бот RoleHub, где лежат основные механики и как модули взаимодействуют друг с другом.

Актуальное состояние проекта:

- стек: `python-telegram-bot`, SQLAlchemy, SQLite по умолчанию;
- UX построен на нижних reply-клавиатурах пользователя;
- lobby-механика реализована как сущности в базе данных, а не как Telegram-группы;
- режим лобби сейчас только RP;
- максимальный размер каждого нового лобби фиксированный: `15` участников;
- роли в RP уникальны внутри одного лобби;
- общение участников идёт через личный чат с ботом;
- кнопка выхода не показывается в reply-клавиатуре, но команда `/leave` выходит из текущего лобби.

## Быстрая Карта

```text
src/
├── bot.py                         # сборка и запуск Telegram Application
├── core/                          # конфиг, БД, логирование
├── models/                        # SQLAlchemy-модели
├── repositories/                  # SQL-запросы и работа с таблицами
├── services/                      # бизнес-логика
├── handlers/                      # Telegram handlers и reply routing
├── keyboards/                     # reply-клавиатуры
├── render/                        # тексты экранов
├── constants/                     # темы, роли, pending-action состояния
└── utils/                         # маленькие утилиты
```

Главная идея архитектуры:

```text
Telegram update
  -> handler
  -> service
  -> repository
  -> SQLAlchemy model / database
  -> render + keyboard
  -> Telegram response
```

Handlers принимают Telegram-события. Services принимают бизнес-решения. Repositories делают запросы в БД. Render и keyboards отвечают за пользовательский интерфейс.

## Точка Входа

### `src/bot.py`

Главный файл сборки приложения.

Что делает:

- вызывает `create_db_tables()`, чтобы создать таблицы;
- читает Telegram token через `get_api_key()`;
- создаёт `Application` из `python-telegram-bot`;
- подключает handlers:
  - `/start`;
  - админку;
  - reply-router главного меню;
  - lobby message handler;
- подключает `post_init(start_lobby_background_tasks)`, чтобы стартовать фоновую очистку истёкших лобби;
- запускает polling в `main()`.

Если нужно добавить новый большой раздел бота, обычно его регистрируют здесь через функцию вида `register_*_handler(application)`.

## Core Слой

### `src/core/config.py`

Отвечает за чтение настроек из окружения.

Обычно здесь находятся функции:

- получить Telegram API key;
- получить URL базы данных;
- получить список owner ids.

Этот файл не должен содержать бизнес-логику. Его задача - отдать конфиг другим модулям.

`OWNER_IDS` из `.env` используется как доступ владельцев для выдачи и снятия админских прав.
Админские права хранятся в БД через `users.role = "admin"`.
Команды `/makeadmin` и `/removeadmin` принимают Telegram ID или `@username` уже известного боту пользователя.

### `src/core/database.py`

Отвечает за подключение к БД.

Ключевые элементы:

- `engine = create_engine(db_url)`;
- `SessionLocal = sessionmaker(..., expire_on_commit=False)`;
- `get_session()` - context manager для работы с SQLAlchemy-сессией;
- `create_db_tables()` - создаёт таблицы через `Base.metadata.create_all(engine)`;
- `_ensure_runtime_columns()` - SQLite-совместимость для старой БД, добавляет поля в `users`, если их ещё нет:
  - `current_lobby_id`;
  - `pending_action`;
  - `create_state`;
  - `display_name`;
  - `news_notifications_enabled`.

Важно: `expire_on_commit=False` нужен, чтобы ORM-объекты можно было безопасно читать после `session.commit()` внутри handler.

### `src/core/logger.py`

Настраивает глобальный logger.

Сейчас лог пишет в `app.log`. Все handlers/services/repositories используют этот logger для ошибок и служебных событий.

## Models Слой

Модели описывают таблицы БД. Это не место для бизнес-логики.

### `src/models/base.py`

Содержит общий SQLAlchemy `Base`.

Все ORM-модели наследуются от `Base`, чтобы SQLAlchemy видел их в общей metadata.

### `src/models/user.py`

Модель `User`.

Хранит:

- Telegram-поля:
  - `telegram_id`;
  - `username`;
  - `first_name`;
  - `last_name`;
  - `language_code`;
  - `display_name`;
  - `is_bot`;
- служебные поля:
  - `role`;
  - `news_notifications_enabled`;
  - `is_registered`;
  - `current_lobby_id`;
  - `pending_action`;
  - `create_state`;
- временные метки:
  - `first_seen_at`;
  - `last_seen_at`;
  - `created_at`;
  - `updated_at`.

Особенно важные поля для lobby:

- `current_lobby_id` показывает, в каком лобби сейчас находится пользователь;
- `pending_action` хранит ожидание следующего текстового сообщения, например ввод кода или поиск роли;
- `create_state` хранит временное состояние создания лобби.
- `display_name` хранит уникальное имя профиля RoleHub, привязанное к Telegram ID.
- `news_notifications_enabled` управляет получением новостных рассылок `/notify`.
- `role` используется для админских прав: `admin` получает доступ к админ-командам.

### `src/models/chat_message.py`

Модель `ChatMessage`.

Хранит Telegram `message_id`, которые бот знает и может попробовать удалить через `/clear` или перед новым `/start`.

Активный экран бота, например главное меню, настройки или экран комнаты, помечается как `is_active_screen=True`.
`/clear` и очистка перед `/start` пытаются удалить все сохранённые сообщения этого чата, кроме текущего активного экрана.
Когда бот показывает новый активный экран, предыдущий активный экран становится обычным очищаемым сообщением.

### `src/models/lobby.py`

Содержит три модели lobby-механики.

#### `Lobby`

Лобби как сущность в БД.

Поля:

- `id`;
- `code` - короткий код лобби;
- `topic` - тема, например `brawl_stars`;
- `mode` - сейчас используется `rp`;
- `owner_id`;
- `max_players` - сейчас для новых лобби всегда `15`;
- `players_count`;
- `privacy` - `public` или `private`;
- `status` - `waiting`, `active`, `closed`;
- `created_at`, `updated_at`;
- `expires_at`;
- `activated_at`;
- `closed_at`.

#### `LobbyMember`

Связь пользователя и лобби.

Поля:

- `lobby_id`;
- `user_id`;
- `role` - выбранная RP-роль;
- `is_owner`;
- `status` - `joined` или `left`;
- `joined_at`;
- `left_at`.

Есть уникальное ограничение `lobby_id + user_id`, чтобы один пользователь не плодил дубликаты членства в одном лобби.

#### `LobbyMessage`

История сообщений активного лобби.

Поля:

- `lobby_id`;
- `sender_id`;
- `message_type` - `text`, `photo`, `sticker`, `voice`;
- `text`;
- `file_id`;
- `created_at`.

## Constants Слой

### `src/constants/topics.py`

Список доступных тем и подписи для кнопок.

Сейчас доступны:

- `brawl_stars`;
- `mlp`.

Roblox удалён из актуального пользовательского сценария.

### `src/constants/roles.py`

Большой справочник RP-ролей.

Что содержит:

- `ROLE_PAGE_SIZE = 10`;
- списки персонажей Brawl Stars и My Little Pony;
- русские транслитерации ролей;
- slug-ключи ролей;
- `ROLES_BY_TOPIC`;
- `ROLE_BUTTONS_BY_TOPIC`;
- `get_role_original_name()`;
- `search_roles()`.

Роли хранятся так, чтобы в БД сохранялся стабильный slug, а пользователю показывалась русская транслитерация.

Пример:

```python
"twilight_sparkle": "Твайлайт Спаркл"
```

Поиск роли работает по:

- русскому имени;
- оригинальному латинскому имени;
- slug.

### `src/constants/pending_actions.py`

Содержит строковые константы pending-state:

- `PENDING_ENTER_LOBBY_CODE`;
- `PENDING_CREATE_ROLE_SEARCH`;
- `PENDING_JOIN_ROLE_SEARCH_PREFIX`.

Эти значения используются в `User.pending_action`.

## Utils Слой

### `src/utils/display_name.py`

Формирует имя пользователя для обычных не-RP мест.

Правило:

- если есть `username`, вернуть `@username`;
- иначе `first_name`;
- иначе `Участник`.

В RP-чате сообщения подписываются ролью, а не Telegram-именем. Это реализовано в `lobby_message_service`.

### `src/utils/invite_code.py`

Генерирует короткий код лобби.

Алфавит исключает похожие символы, чтобы коды было легче читать.

## Repositories Слой

Repositories должны быть тонким SQL-слоем. Они не решают бизнес-правила, а только ищут, создают и возвращают данные.

### `src/repositories/user_repo.py`

Операции с `User`.

Ключевые функции:

- `get_by_telegram_id()`;
- `get_by_id()`;
- `list_users()`;
- `list_all_users()`;
- `get_users_stats()`;
- `create_from_effective_user()`;
- `update_from_effective_user()`.

Используется:

- `/start`;
- reply-router;
- админка;
- lobby handlers.

### `src/repositories/lobby_repo.py`

Операции с `Lobby`.

Ключевые функции:

- `get_by_code()`;
- `get_by_id()`;
- `create()`;
- `find_available()`;
- `list_expired()`;
- `get_current_for_user()`.

`find_available()` ищет public waiting-лобби по теме, где есть место, и исключает лобби, где пользователь уже joined.

### `src/repositories/lobby_member_repo.py`

Операции с участниками лобби.

Ключевые функции:

- `get_member()`;
- `get_joined_member()`;
- `list_joined()`;
- `list_joined_users()`;
- `list_taken_roles()`;
- `is_role_taken()`;
- `create_member()`;
- `first_non_owner_joined()`.

Используется для:

- проверки уникальности ролей;
- списка участников;
- передачи владельца;
- рассылок.

### `src/repositories/lobby_message_repo.py`

Создаёт записи `LobbyMessage`.

Основная функция:

- `create_message()`.

## Services Слой

Services - место бизнес-логики. Именно здесь должны жить правила: кто может войти, когда лобби закрывается, как назначаются роли.

### `src/services/user_service.py`

Сервис синхронизации Telegram-пользователя с БД.

Главная функция:

- `ensure_from_effective_user(session, effective_user)`.

Она:

- возвращает `None`, если в update нет пользователя;
- ищет пользователя по Telegram ID;
- создаёт пользователя, если его ещё нет;
- обновляет Telegram-поля, если пользователь уже есть.

### `src/services/user_state_service.py`

Управляет временными состояниями пользователя.

Функции:

- `set_create_state()`;
- `get_create_state()`;
- `clear_create_state()`;
- `set_pending_action()`;
- `get_pending_action()`;
- `clear_pending_action()`.

Используется в сценариях:

- создание лобби;
- ввод кода;
- поиск роли текстовым сообщением.

### `src/services/lobby_service.py`

Главный бизнес-сервис lobby.

Важные константы:

- `WAITING_TTL = 30 минут`;
- `ACTIVE_TTL = 2 часа`;
- `LOBBY_MAX_PLAYERS = 15`.

Ключевые функции:

- `create_lobby()`;
- `join_lobby()`;
- `leave_lobby()`;
- `start_lobby()`;
- `close_lobby()`;
- `get_lobby_by_code()`;
- `get_current_lobby()`;
- `render_lobby_status()`.

Правила, которые здесь реализованы:

- пользователь не может быть в двух лобби одновременно;
- новое лобби всегда создаётся в режиме `rp`;
- новое лобби всегда получает `max_players = 15`;
- роль обязательна для RP;
- две одинаковые joined-роли в одном лобби запрещены;
- нельзя войти в закрытое, активное или заполненное лобби;
- запуск owner-only, если участников минимум 2;
- при выходе последнего участника лобби закрывается;
- если выходит владелец, владелец передаётся следующему joined-участнику;
- при закрытии лобби у joined-пользователей очищается `current_lobby_id`.

### `src/services/matchmaking_service.py`

Сервис поиска лобби.

Функции:

- `find_available_lobby()`;
- `find_next_lobby()`;
- `quick_join()`.

Сейчас handler часто сам делает проверку RP-роли перед фактическим `join_lobby()`, потому что для RP нужен выбор свободной роли.

### `src/services/lobby_message_service.py`

Сервис сохранения и рассылки сообщений активного лобби.

Что делает:

- превращает Telegram `Message` в `LobbyMessagePayload`;
- сохраняет сообщение в `LobbyMessage`;
- определяет подпись отправителя;
- рассылает сообщение всем другим joined-участникам;
- не отправляет сообщение обратно отправителю;
- ошибки доставки одному участнику логирует, но не ломает рассылку остальным.

В RP подпись отправителя - это роль.

Пример:

```text
💬 Рэйнбоу Дэш:
текст сообщения
```

### `src/services/notification_service.py`

Сервис системных уведомлений участникам лобби.

Функции:

- `notify_lobby_started()`;
- `notify_user_joined()`;
- `notify_user_left()`;
- `notify_lobby_closed()`;
- `notify_owner_changed()`.

В RP уведомления тоже используют роль вместо Telegram-имени.

## Handlers Слой

Handlers принимают Telegram update и решают, какой service вызвать.

### `src/handlers/start.py`

Обработчик `/start`.

Алгоритм:

1. логирует старт;
2. создаёт или обновляет пользователя через `ensure_from_effective_user()`;
3. показывает главное меню через `showMainMenu()`.

### `src/handlers/admin.py`

Админская точка входа.

Что делает:

- команда `/admin`;
- проверяет админские права по `users.role = "admin"` в БД;
- показывает админ-панель;
- подключает `register_admin_users_handlers()`;
- содержит reply-кнопки админ-панели.
- команды `/makeadmin` и `/removeadmin` доступны только владельцам из `OWNER_IDS`.

### `src/handlers/admin_handlers/users.py`

Админские команды по пользователям.

Обычно здесь:

- `/users`;
- `/user <telegram_id>`;
- `/stats`;
- `/export_users`;
- reply-кнопки админ-панели.

Использует `user_repo` для чтения пользователей и статистики.

### `src/handlers/main_menu.py`

Центральный reply-router общего меню.

Главная функция:

- `main_menu_reply_router(update, context)`.

Она обрабатывает точные тексты reply-кнопок:

```text
🎮 Играть
🛍 Магазин
⚙️ Настройки
🆘 Поддержка
```

Перед обработкой кнопки router создаёт или обновляет пользователя в БД.
Игровая кнопка `🎮 Играть` делегируется в `src/handlers/play_lobby.py`.

Остальные разделы, например shop/settings/support, сейчас в основном показывают заглушки.

### `src/handlers/play_lobby.py`

Самый важный файл lobby-механики.

Здесь находятся:

- обработчик нижних reply-кнопок игрового сценария;
- обработчик обычных сообщений в активном лобби;
- обработчик ввода кода лобби;
- обработчик поиска роли сообщением;
- фоновая очистка истёкших лобби.

Основные функции:

- `show_play_menu()`;
- `lobby_message_handler()`;
- `close_expired_lobbies_for_bot()`;
- `register_lobby_message_handler()`.

#### Создание лобби

Текущий поток:

```text
Играть
  -> Создать лобби
  -> выбрать приватность
  -> выбрать тему
  -> выбрать роль
  -> подтверждение
  -> create_lobby()
  -> экран ожидания
```

Выбора режима нет. Выбора количества участников нет. Лобби всегда RP и всегда на 15 участников.

#### Поиск лобби

Поток:

```text
Играть
  -> Найти лобби
  -> выбрать способ: код или тема
  -> выбрать тему или ввести код
  -> find_available_lobby()
  -> найденное лобби
  -> Войти
  -> выбор свободной роли
  -> join_lobby()
```

#### Быстрый вход

Поток:

```text
Играть
  -> Быстрый вход
  -> выбрать тему
  -> найти public waiting lobby
  -> если RP, сначала выбрать свободную роль
  -> join_lobby()
```

#### Вход по коду

Поток:

```text
Играть
  -> Войти по коду
  -> pending_action = enter_lobby_code
  -> следующее текстовое сообщение читается как код
  -> если лобби RP, показать выбор роли
  -> join_lobby()
```

#### Поиск роли сообщением

Для создания:

```text
кнопка `🔎 Найти роль` при создании
  -> pending_action = search_create_role
  -> следующее текстовое сообщение ищет роль
```

Для входа:

```text
кнопка `🔎 Найти роль` при входе в лобби
  -> pending_action = search_join_role:{code}
  -> следующее текстовое сообщение ищет свободную роль
```

Важно: поиск роли обрабатывается до обычной lobby-рассылки, поэтому поисковый текст не улетает участникам.

#### Активное общение

`lobby_message_handler()` обрабатывает:

- текст;
- фото;
- стикер;
- voice.

Алгоритм:

1. найти или создать `User`;
2. проверить pending-action;
3. проверить `current_lobby_id`;
4. проверить `lobby.status == active`;
5. сохранить сообщение;
6. разослать всем другим joined-участникам.

#### Выход из лобби

Кнопка выхода не показывается в пользовательских клавиатурах.
Команда `/leave` вызывает выход из текущего лобби.

## Keyboards Слой

### `src/keyboards/kb_build.py`

Фабрики клавиатур общего меню.

Ключевые функции:

- `_build_reply_keyboard()`;
- `getMainMenuKeyboard()`;
- shop/settings/support keyboards;
- `getBackToMenuKeyboard()`;
- `build_admin_panel()`.

### `src/keyboards/lobby_keyboard.py`

Фабрики клавиатур lobby-механики.

Ключевые функции:

- `get_play_main_reply_keyboard()`;
- `get_find_main_reply_keyboard()`;
- `get_topic_reply_keyboard()`;
- `get_active_lobby_reply_keyboard()` без `/leave`, с кнопками комнаты;
- `get_remove_lobby_reply_keyboard()`;
- error/fallback keyboards.

Здесь же живёт пагинация ролей:

- `_paginate()`;
- `_page_nav()`;

Роли показываются по `ROLE_PAGE_SIZE`, сейчас это 10 кнопок на страницу.

## Render Слой

Render-файлы собирают тексты экранов. Они не должны ходить в БД и не должны менять состояние.

### `src/render/menu.py`

Тексты и отправка общих меню.

Ключевые функции:

- `_render()`;
- `showMainMenu()`;
- `showPlayTopics()`;
- `showTopicActions()`;
- `showShop()`;
- `showSettings()`;
- `showSupport()`;
- `showComingSoon()`;
- `showFaqAnswer()`;
- `showRules()`.

`_render()` отправляет новый активный экран через `reply_text` и прикладывает reply-клавиатуру.

### `src/render/lobby_render.py`

Тексты lobby-экранов.

Ключевые функции:

- `topic_name()`;
- `mode_name()`;
- `privacy_name()`;
- `role_name()`;
- `render_play_main()`;
- `render_create_topic()`;
- `render_create_role()`;
- `render_create_privacy()`;
- `render_create_confirm()`;
- `render_lobby_waiting()`;
- `render_lobby_info()`;
- `render_active_lobby_started()`;
- `render_found_lobby()`;
- `render_join_role()`;
- `render_no_lobby()`;
- `render_quick_no_lobby()`.

## Reply-Кнопки

Все пользовательские и админские меню используют нижнюю reply-клавиатуру Telegram.
Кнопки обрабатываются как точный текст входящего сообщения.

## Основные Сценарии

### Создать лобби

```text
Пользователь нажимает `🎮 Играть`
  -> render_play_main() + нижняя reply-клавиатура
  -> `➕ Создать лобби`
  -> _show_create_privacy()
  -> выбрать тип лобби
  -> выбрать тему
  -> save create_state(topic, mode=rp)
  -> render_create_role()
  -> выбрать роль reply-кнопкой
  -> save create_state(role, max_players=15)
  -> render_create_confirm()
  -> `🚀 Создать лобби`
  -> lobby_service.create_lobby()
  -> render_lobby_waiting()
```

### Найти и войти

```text
`🎮 Играть`
  -> `🔎 Найти лобби`
  -> выбрать способ поиска
  -> выбрать тему или отправить код текстом
  -> matchmaking_service.find_available_lobby()
  -> render_found_lobby()
  -> `✅ Войти`
  -> render_join_role()
  -> выбрать роль reply-кнопкой
  -> lobby_service.join_lobby()
  -> render_lobby_waiting()
```

### Активировать лобби

```text
`▶️ Запустить`
  -> lobby_service.start_lobby()
  -> status = active
  -> expires_at = now + 2 hours
  -> notify_lobby_started()
```

Лобби также может стартовать автоматически, если после входа `players_count == max_players`.

### Общаться

```text
message text/photo/sticker/voice
  -> lobby_message_handler()
  -> check current_lobby_id
  -> check lobby.status == active
  -> payload_from_telegram_message()
  -> send_message_to_lobby()
  -> save LobbyMessage
  -> send to other joined members
```

### Выйти

```text
Сценарий временно отключён.
Игровые клавиатуры не показывают кнопку выхода.
Команда /leave регистрируется в Application и выходит из текущего лобби.
```

### Очистка истёкших лобби

```text
start_lobby_background_tasks()
  -> каждые 60 секунд
  -> lobby_repo.list_expired(now)
  -> close_lobby(reason=expired)
  -> notify_lobby_closed()
```

Сроки:

- waiting lobby: 30 минут;
- active lobby: 2 часа.

## Как Добавлять Новую Механику

### Если нужна новая кнопка

1. Добавить текст кнопки в нужную reply-клавиатуру.
2. Добавить обработку текста кнопки в handler.
3. Если нужен текст экрана, добавить функцию в render.
4. Если есть бизнес-правило, добавить его в service.

### Если нужна новая таблица

1. Создать модель в `src/models/`.
2. Импортировать модель так, чтобы `Base.metadata.create_all()` её увидел.
3. Создать repository.
4. Вызвать repository из service, не напрямую из handler.

### Если нужна новая lobby-операция

Правильный путь:

```text
play_lobby.py handler
  -> lobby_service.py или отдельный service
  -> repository
  -> model
```

Не стоит:

- писать SQL прямо в handler;
- менять ORM-объекты в render;
- держать бизнес-правила в keyboard-файлах;
- отправлять Telegram-сообщения из repository.

## Тесты

### `tests/test_reply_keyboards.py`

Проверяет:

- состав reply-клавиатуры главного меню;
- состав reply-клавиатуры админ-панели;
- кнопки активной комнаты без `/leave`.

### `tests/test_user_repository.py`

Проверяет:

- создание пользователя из Telegram effective_user;
- отсутствие дублей;
- обновление username;
- сохранение `is_registered`;
- поиск по Telegram ID;
- список пользователей и статистику.

### `tests/conftest.py`

Сейчас содержит тест для `get_owner_ids()`.

### `tests/test_registration.py`, `tests/test_start.py`

Минимальные placeholder-тесты.

## Документы В `docs/`

### `docs/PROJECT_STRUCTURE.md`

Старый документ про структуру проекта.

### `docs/23.05_education.md`, `docs/25.05roadmap.md`, `docs/26.05_progress.md`, `docs/26.05_tasks.md`

Рабочие заметки, дорожная карта и прогресс.

### `docs/BOT_ARCHITECTURE_GUIDE.md`

Этот документ. Его стоит обновлять после крупных изменений архитектуры.

## Что Важно Помнить

- Лобби - это запись в БД, не Telegram-группа.
- Пользователь может быть только в одном лобби, это контролируется через `User.current_lobby_id`.
- RP-роль уникальна внутри лобби.
- Сообщения активного лобби идут через бота всем другим joined-участникам.
- В RP подпись сообщения - роль, не Telegram username.
- Все новые лобби создаются с `max_players = 15`.
- Старые пустые placeholder-модули удалены, но `__init__.py` оставлены как пакетные файлы.
- Background cleanup закрывает истёкшие waiting/active лобби.

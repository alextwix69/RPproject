# Тесты проекта

Документ описывает текущие pytest-проверки в директории `tests/`.

## Запуск

Обычная команда:

```bash
pytest
```

Если `pytest` не находится в `PATH`, можно запускать через установленный Python:

```bash
python -m pytest
```

В текущем окружении проверенный запуск выполнялся так:

```powershell
& 'C:\Users\alex\AppData\Local\Programs\Python\Python314\python.exe' -m pytest -q
```

Последний результат:

```text
10 passed
```

Предупреждения связаны с `datetime.utcnow()` в SQLAlchemy-моделях и репозитории. Они не ломают текущую бизнес-логику, но позже лучше заменить на timezone-aware UTC.

## Пользователи, БД и сервисный слой

Файл: `tests/test_user_repository.py`

Эти тесты проверяют бизнес-правило зоны `alextwix`: Telegram-пользователь при взаимодействии с ботом должен создаваться или обновляться через сервисный слой.

- `test_new_effective_user_creates_user` - новый Telegram `effective_user` создает запись пользователя в таблице `users`.
- `test_repeated_effective_user_does_not_create_duplicate` - повторная обработка того же Telegram-пользователя не создает дубль.
- `test_username_updates_on_repeated_interaction` - Telegram-данные пользователя обновляются при повторном взаимодействии.
- `test_is_registered_does_not_reset_on_update` - внутренний флаг `is_registered=True` не сбрасывается при обновлении Telegram-данных.
- `test_get_by_telegram_id_type` - `get_by_telegram_id()` возвращает объект `User`, если запись есть, и `None`, если пользователя нет.

БД в этих тестах:

- используется временная SQLite БД `sqlite:///:memory:`;
- таблицы создаются через `Base.metadata.create_all(bind=engine)`;
- SQLAlchemy `session` создается через `sessionmaker`;
- после изменения данных вызывается `session.commit()`;
- в конце тестов сессия закрывается через `session.close()`.

Основной проверяемый путь:

```text
tests/test_user_repository.py
-> src/services/user_service.py
-> src/repositories/user_repo.py
-> src/models/user.py
-> users
```

## Главное меню и callback-router

Файл: `tests/test_main_menu_callbacks.py`

Эти тесты проверяют чистую бизнес-логику callback-data без Telegram, БД и handlers.

- `test_known_main_menu_callbacks_return_expected_intents` - известные callback-data `main:*` возвращают правильные intent.
- `test_unknown_main_menu_callback_returns_unknown` - неизвестный callback внутри namespace `main` возвращает `MainMenuIntent.UNKNOWN`.
- `test_foreign_callback_namespace_returns_unknown` - callback из чужого namespace возвращает `MainMenuIntent.UNKNOWN`.
- `test_empty_callback_returns_unknown` - пустая callback-data не ломает router и возвращает `MainMenuIntent.UNKNOWN`.
- `test_response_text_exists_for_every_intent` - для каждого `MainMenuIntent` есть непустой UX-текст ответа.

Проверяемый путь:

```text
tests/test_main_menu_callbacks.py
-> src/callbacks/main_menu.py
```

## Стартовый сценарий

Файл: `tests/test_start.py`

Сейчас файл содержит описание будущих проверок команды `/start`, но исполняемых тестов в нем пока нет.

Что стоит добавить дальше:

- `/start` открывает SQLAlchemy session через `get_session()`;
- `/start` вызывает `ensure_user_from_effective_user(...)`;
- при успешном сохранении выполняется `session.commit()`;
- при ошибке выполняется `session.rollback()`;
- пользователю отправляется приветствие и главное меню.

## Регистрация

Файл: `tests/test_registration.py`

Сейчас файл содержит только заготовку. Исполняемых тестов регистрации пока нет.

## Конфигурация pytest

Файл: `tests/conftest.py`

В файле лежат общие настройки и будущие фикстуры pytest. Сейчас там есть проверка `test_get_admin_ids`, но `conftest.py` не является обычным тестовым модулем для pytest-collection, поэтому эту проверку лучше перенести в отдельный файл, например:

```text
tests/test_config.py
```

## Итого

Исполняемых тестов сейчас: `10`.

- `5` тестов пользовательского service/repository слоя;
- `5` тестов callback-router главного меню;
- `0` тестов `/start`;
- `0` тестов регистрации.

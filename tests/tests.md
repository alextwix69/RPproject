# Тесты проекта

## Конфигурация

- `test_get_admin_ids` - проверяет, что `get_admin_ids()` возвращает список ID администраторов из переменной окружения `ADMIN_IDS` в виде чисел.

## Главное меню

- `test_menu_items_not_empty` - проверяет, что `get_menu_items()` возвращает непустой список кнопок главного меню.
- `test_button_text_not_empty` - проверяет, что для каждой кнопки главного меню `get_button_text()` возвращает непустой текст.
- `test_known_main_menu_callbacks_return_expected_intents` - проверяет соответствие известных callback-data главного меню нужным intent: регистрация, профиль, лобби, помощь.
- `test_unknown_main_menu_callback_returns_unknown` - проверяет, что неизвестный callback в namespace `main` возвращает `MainMenuIntent.UNKNOWN`.
- `test_foreign_callback_namespace_returns_unknown` - проверяет, что callback из чужого namespace возвращает `MainMenuIntent.UNKNOWN`.
- `test_empty_callback_returns_unknown` - проверяет, что пустая callback-data не ломает роутер и возвращает `MainMenuIntent.UNKNOWN`.
- `test_response_text_exists_for_every_intent` - проверяет, что для каждого `MainMenuIntent` есть непустой текст ответа.

## Пользователи и репозиторий

- `test_new_effective_user_creates_user` - проверяет, что новый Telegram `effective_user` создает пользователя в базе данных.
- `test_repeated_effective_user_does_not_create_duplicate` - проверяет, что повторная обработка того же Telegram-пользователя не создает дубль.
- `test_username_updates_on_repeated_interaction` - проверяет, что username обновляется при повторном взаимодействии пользователя.
- `test_is_registered_does_not_reset_on_update` - проверяет, что флаг `is_registered=True` не сбрасывается при обновлении Telegram-данных.

## Стартовый сценарий

- `test_start.py` - сейчас содержит только описание будущих проверок команды `/start`; исполняемых тестов в файле пока нет.

Всего: 12 исполняемых тестов.

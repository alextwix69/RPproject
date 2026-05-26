from src.callbacks.main_menu import (
    MAIN_MENU_RESPONSE_TEXTS,
    MainMenuIntent,
    get_main_menu_response_text,
    resolve_main_menu_callback,
)


def test_known_main_menu_callbacks_return_expected_intents():
    """Каждый известный callback главного меню возвращает свой intent."""

    assert resolve_main_menu_callback("main:register") == MainMenuIntent.REGISTER
    assert resolve_main_menu_callback("main:profile") == MainMenuIntent.PROFILE
    assert resolve_main_menu_callback("main:lobby") == MainMenuIntent.LOBBY
    assert resolve_main_menu_callback("main:help") == MainMenuIntent.HELP


def test_unknown_main_menu_callback_returns_unknown():
    """Неизвестный callback в namespace main не ломает router."""

    assert resolve_main_menu_callback("main:unknown") == MainMenuIntent.UNKNOWN


def test_foreign_callback_namespace_returns_unknown():
    """Чужой namespace тоже считается неизвестным для главного меню."""

    assert resolve_main_menu_callback("profile:open") == MainMenuIntent.UNKNOWN


def test_empty_callback_returns_unknown():
    """Пустая callback-data не должна ломать router."""

    assert resolve_main_menu_callback("") == MainMenuIntent.UNKNOWN


def test_response_text_exists_for_every_intent():
    """Для каждого intent есть UX-текст, который handler сможет отправить пользователю."""

    for intent in MainMenuIntent:
        assert intent in MAIN_MENU_RESPONSE_TEXTS
        assert get_main_menu_response_text(intent)
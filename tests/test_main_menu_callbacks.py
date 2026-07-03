import pytest

from src.callbacks.main_menu import (
    MAIN_MENU_RESPONSE_TEXTS,
    MainMenuIntent,
    get_main_menu_response_text,
    resolve_main_menu_callback,
)
from src.keyboards.kb_build import (
    build_admin_panel,
    getMainMenuKeyboard,
    getPlayTopicsKeyboard,
    getTopicActionsKeyboard,
)


def test_known_main_menu_callbacks_return_expected_intents():
    """Каждый известный callback главного меню возвращает свой intent."""

    assert resolve_main_menu_callback("menu:main") == MainMenuIntent.MAIN
    assert resolve_main_menu_callback("menu:play") == MainMenuIntent.PLAY
    assert resolve_main_menu_callback("menu:shop") == MainMenuIntent.SHOP
    assert resolve_main_menu_callback("menu:settings") == MainMenuIntent.SETTINGS
    assert resolve_main_menu_callback("menu:support") == MainMenuIntent.SUPPORT


def test_unknown_main_menu_callback_returns_unknown():
    """Неизвестный callback в namespace main не ломает router."""

    assert resolve_main_menu_callback("menu:unknown") == MainMenuIntent.UNKNOWN


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


def _callback_data(markup):
    return [
        button.callback_data
        for row in markup.inline_keyboard
        for button in row
    ]


def test_main_menu_keyboard_uses_rolehub_callbacks():
    assert _callback_data(getMainMenuKeyboard()) == [
        "menu:play",
        "menu:shop",
        "menu:settings",
        "menu:support",
    ]


def test_play_topic_keyboard_uses_expected_callbacks():
    assert _callback_data(getPlayTopicsKeyboard()) == [
        "play:topic:brawl_stars",
        "play:topic:mlp",
        "menu:main",
    ]


def test_topic_actions_keyboard_has_back_and_menu_callbacks():
    assert _callback_data(getTopicActionsKeyboard("mlp")) == [
        "play:find:mlp",
        "play:create:mlp",
        "play:rooms:mlp",
        "play:back:topics",
        "menu:main",
    ]


def test_admin_panel_uses_expected_callbacks():
    assert _callback_data(build_admin_panel()) == [
        "admin:users",
        "admin:stats",
        "admin:export_users",
    ]

from src.keyboards.kb_build import BTN_RETURN_TO_ACTIVE_LOBBY, build_admin_panel, getMainMenuKeyboard
from src.keyboards.lobby_keyboard import (
    BTN_BACK,
    BTN_MAIN_MENU,
    get_active_lobby_reply_keyboard,
    get_create_role_inline_keyboard,
    get_navigation_reply_keyboard,
    get_play_main_reply_keyboard,
    get_topic_inline_keyboard,
)


def _reply_texts(markup):
    return [
        button.text
        for row in markup.keyboard
        for button in row
    ]


def test_main_menu_keyboard_uses_reply_buttons():
    assert _reply_texts(getMainMenuKeyboard()) == [
        "🎮 Играть",
        "🛍 Магазин",
        "⚙️ Настройки",
        "🆘 Поддержка",
    ]


def test_main_menu_keyboard_can_include_active_lobby_return():
    assert _reply_texts(getMainMenuKeyboard(include_return_to_lobby=True))[0] == BTN_RETURN_TO_ACTIVE_LOBBY


def test_admin_panel_uses_reply_buttons():
    assert _reply_texts(build_admin_panel()) == [
        "Пользователи",
        "Статистика",
        "Экспорт CSV",
        "Новостная рассылка",
        "Права админов",
        "🏠 Главное меню",
    ]


def test_active_lobby_reply_keyboard_has_room_controls_without_leave():
    buttons = _reply_texts(get_active_lobby_reply_keyboard())

    assert buttons[:2] == ["👥 Участники", "ℹ️ Инфо"]
    assert "/leave" not in buttons


def test_choice_reply_keyboard_has_only_navigation_buttons():
    assert _reply_texts(get_navigation_reply_keyboard()) == [BTN_BACK, BTN_MAIN_MENU]


def test_play_keyboard_can_include_active_lobby_return():
    assert _reply_texts(get_play_main_reply_keyboard(include_return_to_lobby=True))[0] == BTN_RETURN_TO_ACTIVE_LOBBY


def test_topic_choices_are_inline_buttons():
    buttons = [
        button
        for row in get_topic_inline_keyboard().inline_keyboard
        for button in row
    ]

    assert [button.text for button in buttons] == ["⭐ Brawl Stars", "🦄 My Little Pony"]
    assert [button.callback_data for button in buttons] == ["lobby:topic:brawl_stars", "lobby:topic:mlp"]


def test_role_choices_are_inline_buttons():
    first_button = get_create_role_inline_keyboard("brawl_stars").inline_keyboard[0][0]

    assert first_button.text == "8-Бит"
    assert first_button.callback_data == "lobby:create_role:8_bit"

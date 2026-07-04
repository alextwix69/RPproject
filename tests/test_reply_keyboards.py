from src.keyboards.kb_build import build_admin_panel, getMainMenuKeyboard
from src.keyboards.lobby_keyboard import get_active_lobby_reply_keyboard


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

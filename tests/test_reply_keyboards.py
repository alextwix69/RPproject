from src.keyboards.kb_build import (
    BTN_ADD_FOUND_FRIEND,
    BTN_FIND_FRIEND,
    BTN_PROFILE_AVATAR,
    BTN_RETURN_TO_ACTIVE_LOBBY,
    BTN_VIEW_FOUND_PROFILE,
    build_admin_panel,
    getFoundFriendKeyboard,
    getFriendsKeyboard,
    getMainMenuKeyboard,
    getSettingsProfileKeyboard,
    getSupportKeyboard,
    normalize_button_text,
)
from src.keyboards.lobby_keyboard import (
    BTN_BACK,
    BTN_MAIN_MENU,
    get_active_lobby_reply_keyboard,
    get_create_role_inline_keyboard,
    get_navigation_reply_keyboard,
    get_play_main_reply_keyboard,
    get_lobby_waiting_reply_keyboard,
    get_topic_inline_keyboard,
    normalize_lobby_button_text,
)
from src.services.user_state_service import GENERAL_MENU_SCENES, is_general_menu_scene


def _reply_texts(markup):
    return [
        button.text
        for row in markup.keyboard
        for button in row
    ]


def test_main_menu_keyboard_uses_reply_buttons():
    assert _reply_texts(getMainMenuKeyboard()) == [
        "🌌 Войти в мир",
        "🤝 Друзья и герои",
        "💎 Лавка сокровищ",
        "⚙️ Настройки героя",
        "🪄 Магическая поддержка",
    ]


def test_main_menu_keyboard_can_include_active_lobby_return():
    assert _reply_texts(getMainMenuKeyboard(include_return_to_lobby=True))[0] == BTN_RETURN_TO_ACTIVE_LOBBY


def test_support_keyboard_only_has_admin_contact_and_navigation():
    assert _reply_texts(getSupportKeyboard()) == [
        "👑 Связаться с администратором",
        "↩️ Назад",
        "🏰 Главное меню",
    ]


def test_old_general_menu_buttons_are_normalized_to_new_labels():
    assert normalize_button_text("🎮 Играть") == "🌌 Войти в мир"
    assert normalize_button_text("🏠 Главное меню") == "🏰 Главное меню"
    assert normalize_button_text("👤 Связаться с администратором") == "👑 Связаться с администратором"


def test_old_lobby_buttons_are_normalized_to_new_labels():
    assert normalize_lobby_button_text("➕ Создать лобби") == "✨ Создать свой мир"
    assert normalize_lobby_button_text("🚪 Выйти") == "🚪 Покинуть мир"
    assert normalize_lobby_button_text("⬅️ Назад") == "↩️ Назад"


def test_admin_panel_uses_reply_buttons():
    assert _reply_texts(build_admin_panel()) == [
        "👥 Пользователи",
        "📊 Статистика",
        "📜 Экспорт CSV",
        "📣 Новостная рассылка",
        "👑 Права админов",
        "🏰 Главное меню",
    ]


def test_profile_keyboard_has_avatar_edit_button():
    buttons = _reply_texts(getSettingsProfileKeyboard())

    assert "✍️ Имя героя" in buttons
    assert BTN_PROFILE_AVATAR in buttons


def test_friends_keyboard_starts_search_flow():
    assert BTN_FIND_FRIEND in _reply_texts(getFriendsKeyboard())


def test_found_friend_keyboard_has_profile_and_add_actions():
    buttons = _reply_texts(getFoundFriendKeyboard())

    assert BTN_VIEW_FOUND_PROFILE in buttons
    assert BTN_ADD_FOUND_FRIEND in buttons


def test_general_menu_back_scenes_are_classified_for_main_menu_return():
    expected_scenes = {
        "shop",
        "shop_premium",
        "settings",
        "settings_profile",
        "support",
        "support_faq",
        "support_faq_answer",
        "friends",
        "friend_found",
        "friend_profile",
    }

    assert GENERAL_MENU_SCENES == expected_scenes
    assert all(is_general_menu_scene(scene) for scene in expected_scenes)
    assert not is_general_menu_scene("create_role")


def test_active_lobby_reply_keyboard_has_room_controls_and_exit_button():
    buttons = _reply_texts(get_active_lobby_reply_keyboard())

    assert buttons[:2] == ["👥 Герои", "📜 О мире"]
    assert "🚪 Покинуть мир" in buttons
    assert "/leave" not in buttons


def test_waiting_lobby_keyboard_does_not_show_refresh_button():
    buttons = _reply_texts(get_lobby_waiting_reply_keyboard(is_owner=True))

    assert "✨ Обновить мир" not in buttons
    assert "🚀 Начать приключение" not in buttons
    assert "🚪 Покинуть мир" in buttons


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

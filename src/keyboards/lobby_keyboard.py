"""Inline-клавиатуры lobby-механики."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.constants.roles import ROLE_BUTTONS_BY_TOPIC
from src.constants.topics import TOPIC_BUTTONS


def _build(rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=text, callback_data=data) for text, data in row] for row in rows]
    )


def get_play_main_keyboard() -> InlineKeyboardMarkup:
    return _build(
        [
            [("🔎 Найти лобби", "play:find")],
            [("➕ Создать лобби", "play:create")],
            [("⚡ Быстрый вход", "play:quick")],
            [("🔑 Войти по коду", "play:code")],
            [("⬅️ Назад", "menu:main")],
        ]
    )


def get_topic_keyboard(prefix: str, back_callback: str = "play:main") -> InlineKeyboardMarkup:
    return _build(
        [
            [(label, f"{prefix}:topic:{topic}")]
            for topic, label in TOPIC_BUTTONS.items()
        ]
        + [[("⬅️ Назад", back_callback), ("🏠 Меню", "menu:main")]]
    )


def get_create_mode_keyboard() -> InlineKeyboardMarkup:
    return _build(
        [
            [("💬 Обычное общение", "create:mode:chat")],
            [("🎭 Ролевая игра", "create:mode:rp")],
            [("⬅️ Назад", "create:back:topic"), ("🏠 Меню", "menu:main")],
        ]
    )


def get_create_role_keyboard(topic: str) -> InlineKeyboardMarkup:
    rows = [[button] for button in ROLE_BUTTONS_BY_TOPIC.get(topic, [])]
    rows.append([("🎲 Случайная", "create:role:random")])
    rows.append([("⬅️ Назад", "create:back:mode"), ("🏠 Меню", "menu:main")])
    return _build(rows)


def get_create_size_keyboard(back_callback: str = "create:back:role_or_mode") -> InlineKeyboardMarkup:
    return _build(
        [
            [("2 игрока", "create:size:2"), ("3 игрока", "create:size:3")],
            [("4 игрока", "create:size:4"), ("5 игроков", "create:size:5")],
            [("⬅️ Назад", back_callback), ("🏠 Меню", "menu:main")],
        ]
    )


def get_create_privacy_keyboard() -> InlineKeyboardMarkup:
    return _build(
        [
            [("🌍 Открытое", "create:privacy:public")],
            [("🔒 Приватное", "create:privacy:private")],
            [("⬅️ Назад", "create:back:size"), ("🏠 Меню", "menu:main")],
        ]
    )


def get_create_confirm_keyboard() -> InlineKeyboardMarkup:
    return _build(
        [
            [("🚀 Создать лобби", "create:confirm")],
            [("✏️ Изменить", "create:edit")],
            [("⬅️ Назад", "create:back:privacy"), ("🏠 Меню", "menu:main")],
        ]
    )


def get_lobby_waiting_keyboard(code: str, is_owner: bool) -> InlineKeyboardMarkup:
    rows = [[("🔄 Обновить", f"lobby:refresh:{code}")]]
    if is_owner:
        rows.append([("📨 Пригласить", f"lobby:invite:{code}")])
        rows.append([("▶️ Запустить", f"lobby:start:{code}")])
        rows.append([("🏁 Закрыть", f"lobby:close:{code}")])
    rows.append([("🚪 Выйти", f"lobby:leave:{code}")])
    return _build(rows)


def get_found_lobby_keyboard(code: str, topic: str) -> InlineKeyboardMarkup:
    return _build(
        [
            [("✅ Войти", f"lobby:join:{code}")],
            [("🔄 Следующее", f"find:next:{topic}:{code}")],
            [("⬅️ Назад", "find:topic_menu"), ("🏠 Меню", "menu:main")],
        ]
    )


def get_no_lobby_keyboard(
    topic: str,
    retry_callback: str,
    back_callback: str = "find:topic_menu",
) -> InlineKeyboardMarkup:
    return _build(
        [
            [("➕ Создать лобби", f"create:from_find:{topic}")],
            [("🔄 Искать снова", retry_callback)],
            [("⬅️ Назад", back_callback), ("🏠 Меню", "menu:main")],
        ]
    )


def get_code_entry_keyboard() -> InlineKeyboardMarkup:
    return _build([[("⬅️ Назад", "play:main")], [("🏠 Главное меню", "menu:main")]])


def get_invalid_code_keyboard() -> InlineKeyboardMarkup:
    return _build([[("🔁 Попробовать ещё", "play:code")], [("🏠 Главное меню", "menu:main")]])


def get_active_lobby_keyboard(code: str, is_owner: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [("👥 Участники", f"lobby:members:{code}")],
        [("ℹ️ Инфо", f"lobby:info:{code}")],
    ]
    if is_owner:
        rows.append([("🏁 Закрыть", f"lobby:close:{code}")])
    rows.append([("🚪 Выйти", f"lobby:leave:{code}")])
    return _build(rows)


def get_lobby_members_keyboard(code: str) -> InlineKeyboardMarkup:
    return _build([[("⬅️ Назад", f"lobby:info:{code}")], [("🚪 Выйти", f"lobby:leave:{code}")]])


def get_already_in_lobby_keyboard() -> InlineKeyboardMarkup:
    return _build(
        [
            [("Вернуться в лобби", "lobby:info_current")],
            [("🚪 Выйти из лобби", "lobby:leave_current")],
            [("🏠 Главное меню", "menu:main")],
        ]
    )


def get_lobby_full_keyboard() -> InlineKeyboardMarkup:
    return _build(
        [
            [("🔎 Найти другое", "play:find")],
            [("➕ Создать своё", "play:create")],
            [("🏠 Главное меню", "menu:main")],
        ]
    )


def get_leave_done_keyboard() -> InlineKeyboardMarkup:
    return _build([[("🎮 Играть", "menu:play")], [("🏠 Главное меню", "menu:main")]])


def get_closed_lobby_keyboard() -> InlineKeyboardMarkup:
    return _build([[("🎮 Играть", "menu:play")], [("🏠 Главное меню", "menu:main")]])

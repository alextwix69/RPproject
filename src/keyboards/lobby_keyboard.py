"""Клавиатуры lobby-механики."""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from src.constants.roles import ROLE_PAGE_SIZE, ROLES_BY_TOPIC
from src.constants.topics import TOPIC_BUTTONS

BTN_BACK = "↩️ Назад"
BTN_MAIN_MENU = "🏰 Главное меню"
BTN_CREATE_LOBBY = "✨ Создать свой мир"
BTN_FIND_LOBBY = "🔎 Найти мир"
BTN_SEARCH_BY_CODE = "🔑 Войти по волшебному коду"
BTN_SELECT_TOPIC = "🌌 Выбрать вселенную"
BTN_PUBLIC = "🌍 Открытый мир"
BTN_PRIVATE = "🔒 Тайный мир"
BTN_FIND_ROLE = "🔎 Найти героя"
BTN_RANDOM_ROLE = "🎲 Судьба выберет роль"
BTN_RANDOM_FREE_ROLE = "🎲 Случайная свободная роль"
BTN_CREATE_CONFIRM = "👑 Открыть мир"
BTN_EDIT = "✏️ Изменить выбор"
BTN_REFRESH = "✨ Обновить мир"
BTN_INVITE = "💌 Позвать героев"
BTN_START = "🚀 Начать приключение"
BTN_CLOSE = "🌙 Закрыть мир"
BTN_LEAVE = "🚪 Покинуть мир"
BTN_JOIN = "⚔️ Войти в мир"
BTN_NEXT = "🔮 Следующий мир"
BTN_MEMBERS = "👥 Герои"
BTN_INFO = "📜 О мире"
BTN_SEARCH_AGAIN = "🔄 Искать снова"
BTN_FIND_ANOTHER = "🔮 Найти другой мир"
BTN_CREATE_OWN = "✨ Создать свой мир"
BTN_PLAY = "🌌 Войти в мир"
BTN_SEARCH_MORE = "🌟 Искать ещё"
BTN_TRY_AGAIN = "✨ Попробовать снова"
BTN_RETURN_TO_LOBBY = "↩️ Вернуться в свой мир"

LEGACY_LOBBY_BUTTON_ALIASES = {
    "⬅️ Назад": BTN_BACK,
    "🏠 Главное меню": BTN_MAIN_MENU,
    "➕ Создать лобби": BTN_CREATE_LOBBY,
    "🔎 Найти лобби": BTN_FIND_LOBBY,
    "🔑 Поиск лобби по коду": BTN_SEARCH_BY_CODE,
    "🎯 Выбор темы": BTN_SELECT_TOPIC,
    "🌍 Публичное": BTN_PUBLIC,
    "🔒 Приватное": BTN_PRIVATE,
    "🔎 Найти роль": BTN_FIND_ROLE,
    "🎲 Случайная": BTN_RANDOM_ROLE,
    "🎲 Случайная свободная": BTN_RANDOM_FREE_ROLE,
    "🚀 Создать лобби": BTN_CREATE_CONFIRM,
    "✏️ Изменить": BTN_EDIT,
    "🔄 Обновить": BTN_REFRESH,
    "📨 Пригласить": BTN_INVITE,
    "▶️ Запустить": BTN_START,
    "🏁 Закрыть": BTN_CLOSE,
    "🚪 Выйти": BTN_LEAVE,
    "✅ Войти": BTN_JOIN,
    "🔄 Следующее": BTN_NEXT,
    "👥 Участники": BTN_MEMBERS,
    "ℹ️ Инфо": BTN_INFO,
    "🔎 Найти другое": BTN_FIND_ANOTHER,
    "➕ Создать своё": BTN_CREATE_OWN,
    "🎮 Играть": BTN_PLAY,
    "🔁 Искать ещё": BTN_SEARCH_MORE,
    "🔁 Попробовать ещё": BTN_TRY_AGAIN,
    "↩️ Вернуться в активное лобби": BTN_RETURN_TO_LOBBY,
}


def normalize_lobby_button_text(text: str) -> str:
    return LEGACY_LOBBY_BUTTON_ALIASES.get(text, text)

CB_TOPIC_PREFIX = "lobby:topic:"
CB_CREATE_ROLE_PREFIX = "lobby:create_role:"
CB_CREATE_ROLE_PAGE_PREFIX = "lobby:create_role_page:"
CB_JOIN_ROLE_PREFIX = "lobby:join_role:"
CB_JOIN_ROLE_PAGE_PREFIX = "lobby:join_role_page:"
CB_CREATE_SEARCH_ROLE_PREFIX = "lobby:create_search_role:"
CB_JOIN_SEARCH_ROLE_PREFIX = "lobby:join_search_role:"
CB_LOBBY_SELECT_PREFIX = "lobby:select:"
CB_LOBBY_LIST_PAGE_PREFIX = "lobby:list_page:"
CB_FIND_ROLE = "lobby:find_role"
CB_RANDOM_ROLE = "lobby:random_role"
CB_RANDOM_FREE_ROLE = "lobby:random_free_role"
CB_SEARCH_MORE = "lobby:search_more"


def _reply(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери свой путь ✨",
    )


def _with_nav(rows: list[list[str]]) -> list[list[str]]:
    return rows + [[BTN_BACK, BTN_MAIN_MENU]]


def get_play_main_reply_keyboard(include_return_to_lobby: bool = False) -> ReplyKeyboardMarkup:
    rows = []
    if include_return_to_lobby:
        rows.append([BTN_RETURN_TO_LOBBY])
    rows.append([BTN_CREATE_LOBBY, BTN_FIND_LOBBY])
    return _reply(_with_nav(rows))


def get_find_main_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_SEARCH_BY_CODE], [BTN_SELECT_TOPIC]]))


def get_navigation_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([]))


def get_topic_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[label] for label in TOPIC_BUTTONS.values()]))


def get_topic_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(label, callback_data=f"{CB_TOPIC_PREFIX}{topic}")]
            for topic, label in TOPIC_BUTTONS.items()
        ]
    )


def get_create_role_reply_keyboard(topic: str, page: int = 0) -> ReplyKeyboardMarkup:
    roles = list(ROLES_BY_TOPIC.get(topic, {}).items())
    page_roles, page, pages_count = _paginate(roles, page)
    rows = [[label] for _role, label in page_roles]
    nav = _reply_page_nav(page, pages_count)
    if nav:
        rows.append(nav)
    rows.append([BTN_FIND_ROLE])
    rows.append([BTN_RANDOM_ROLE])
    return _reply(_with_nav(rows))


def get_create_role_inline_keyboard(topic: str, page: int = 0) -> InlineKeyboardMarkup:
    roles = list(ROLES_BY_TOPIC.get(topic, {}).items())
    page_roles, page, pages_count = _paginate(roles, page)
    rows = [
        [InlineKeyboardButton(label, callback_data=f"{CB_CREATE_ROLE_PREFIX}{role}")]
        for role, label in page_roles
    ]
    nav = _inline_page_nav(page, pages_count, CB_CREATE_ROLE_PAGE_PREFIX)
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(BTN_FIND_ROLE, callback_data=CB_FIND_ROLE)])
    rows.append([InlineKeyboardButton(BTN_RANDOM_ROLE, callback_data=CB_RANDOM_ROLE)])
    return InlineKeyboardMarkup(rows)


def get_create_privacy_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_PUBLIC, BTN_PRIVATE]]))


def get_create_confirm_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_CREATE_CONFIRM], [BTN_EDIT]]))


def get_lobby_waiting_reply_keyboard(is_owner: bool) -> ReplyKeyboardMarkup:
    rows = []
    if is_owner:
        rows.append([BTN_INVITE])
        rows.append([BTN_CLOSE])
    rows.append([BTN_LEAVE])
    return _reply(_with_nav(rows))


def get_found_lobby_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_JOIN], [BTN_NEXT]]))


def get_join_role_reply_keyboard(
    code: str,
    topic: str,
    taken_roles: set[str],
    page: int = 0,
) -> ReplyKeyboardMarkup:
    roles = [
        (role, label)
        for role, label in ROLES_BY_TOPIC.get(topic, {}).items()
        if role not in taken_roles
    ]
    page_roles, page, pages_count = _paginate(roles, page)
    rows = [[label] for _role, label in page_roles]
    nav = _reply_page_nav(page, pages_count)
    if nav:
        rows.append(nav)
    if rows:
        rows.append([BTN_FIND_ROLE])
        rows.append([BTN_RANDOM_FREE_ROLE])
    return _reply(_with_nav(rows))


def get_join_role_inline_keyboard(
    code: str,
    topic: str,
    taken_roles: set[str],
    page: int = 0,
) -> InlineKeyboardMarkup:
    roles = [
        (role, label)
        for role, label in ROLES_BY_TOPIC.get(topic, {}).items()
        if role not in taken_roles
    ]
    page_roles, page, pages_count = _paginate(roles, page)
    rows = [
        [InlineKeyboardButton(label, callback_data=f"{CB_JOIN_ROLE_PREFIX}{role}")]
        for role, label in page_roles
    ]
    nav = _inline_page_nav(page, pages_count, CB_JOIN_ROLE_PAGE_PREFIX)
    if nav:
        rows.append(nav)
    if rows:
        rows.append([InlineKeyboardButton(BTN_FIND_ROLE, callback_data=CB_FIND_ROLE)])
        rows.append([InlineKeyboardButton(BTN_RANDOM_FREE_ROLE, callback_data=CB_RANDOM_FREE_ROLE)])
    return InlineKeyboardMarkup(rows)


def get_role_search_results_reply_keyboard(results: list[tuple[str, str]]) -> ReplyKeyboardMarkup:
    rows = [[label] for _role, label in results[:ROLE_PAGE_SIZE]]
    rows.append([BTN_SEARCH_MORE])
    return _reply(_with_nav(rows))


def get_create_role_search_results_inline_keyboard(results: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(label, callback_data=f"{CB_CREATE_SEARCH_ROLE_PREFIX}{role}")]
        for role, label in results[:ROLE_PAGE_SIZE]
    ]
    rows.append([InlineKeyboardButton(BTN_SEARCH_MORE, callback_data=CB_SEARCH_MORE)])
    return InlineKeyboardMarkup(rows)


def get_join_role_search_results_inline_keyboard(results: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(label, callback_data=f"{CB_JOIN_SEARCH_ROLE_PREFIX}{role}")]
        for role, label in results[:ROLE_PAGE_SIZE]
    ]
    rows.append([InlineKeyboardButton(BTN_SEARCH_MORE, callback_data=CB_SEARCH_MORE)])
    return InlineKeyboardMarkup(rows)


def get_lobby_list_inline_keyboard(
    lobbies: list[tuple[str, str]],
    page: int,
    pages_count: int,
) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(label, callback_data=f"{CB_LOBBY_SELECT_PREFIX}{code}")]
        for code, label in lobbies
    ]
    nav = _inline_page_nav(page, pages_count, CB_LOBBY_LIST_PAGE_PREFIX)
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(rows)


def get_role_search_prompt_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([]))


def get_no_lobby_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_CREATE_LOBBY], [BTN_SEARCH_AGAIN]]))


def get_code_entry_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([]))


def get_invalid_code_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_TRY_AGAIN]]))


def get_active_lobby_reply_keyboard(is_owner: bool = False) -> ReplyKeyboardMarkup:
    rows = [[BTN_MEMBERS, BTN_INFO]]
    if is_owner:
        rows.append([BTN_CLOSE])
    rows.append([BTN_LEAVE])
    return _reply(_with_nav(rows))


def get_lobby_info_reply_keyboard(is_owner: bool = False) -> ReplyKeyboardMarkup:
    rows = [[BTN_MEMBERS]]
    if is_owner:
        rows.append([BTN_CLOSE])
    rows.append([BTN_LEAVE])
    return _reply(_with_nav(rows))


def get_lobby_members_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([]))


def get_already_in_lobby_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_RETURN_TO_LOBBY]]))


def get_lobby_full_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_FIND_ANOTHER], [BTN_CREATE_OWN]]))


def get_done_reply_keyboard() -> ReplyKeyboardMarkup:
    return _reply(_with_nav([[BTN_PLAY]]))


def get_remove_lobby_reply_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def role_by_label(topic: str | None, label: str) -> str | None:
    for role, role_label in ROLES_BY_TOPIC.get(topic or "", {}).items():
        if role_label == label:
            return role
    return None


def topic_by_label(label: str) -> str | None:
    for topic, topic_label in TOPIC_BUTTONS.items():
        if topic_label == label:
            return topic
    return None


def _paginate(items, page: int):
    pages_count = max(1, (len(items) + ROLE_PAGE_SIZE - 1) // ROLE_PAGE_SIZE)
    safe_page = min(max(0, page), pages_count - 1)
    start = safe_page * ROLE_PAGE_SIZE
    return items[start:start + ROLE_PAGE_SIZE], safe_page, pages_count


def _reply_page_nav(page: int, pages_count: int) -> list[str]:
    if pages_count <= 1:
        return []

    row = []
    if page > 0:
        row.append("◀️")
    row.append(f"{page + 1}/{pages_count}")
    if page < pages_count - 1:
        row.append("▶️")
    return row


def _inline_page_nav(page: int, pages_count: int, callback_prefix: str) -> list[InlineKeyboardButton]:
    if pages_count <= 1:
        return []

    row = []
    if page > 0:
        row.append(InlineKeyboardButton("◀️", callback_data=f"{callback_prefix}{page - 1}"))
    row.append(InlineKeyboardButton(f"{page + 1}/{pages_count}", callback_data=f"{callback_prefix}{page}"))
    if page < pages_count - 1:
        row.append(InlineKeyboardButton("▶️", callback_data=f"{callback_prefix}{page + 1}"))
    return row

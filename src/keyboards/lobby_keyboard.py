"""Клавиатуры lobby-механики."""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from src.constants.roles import ROLE_PAGE_SIZE, ROLES_BY_TOPIC
from src.constants.topics import TOPIC_BUTTONS

BTN_BACK = "⬅️ Назад"
BTN_MAIN_MENU = "🏠 Главное меню"
BTN_CREATE_LOBBY = "➕ Создать лобби"
BTN_FIND_LOBBY = "🔎 Найти лобби"
BTN_SEARCH_BY_CODE = "🔑 Поиск лобби по коду"
BTN_SELECT_TOPIC = "🎯 Выбор темы"
BTN_PUBLIC = "🌍 Публичное"
BTN_PRIVATE = "🔒 Приватное"
BTN_FIND_ROLE = "🔎 Найти роль"
BTN_RANDOM_ROLE = "🎲 Случайная"
BTN_RANDOM_FREE_ROLE = "🎲 Случайная свободная"
BTN_CREATE_CONFIRM = "🚀 Создать лобби"
BTN_EDIT = "✏️ Изменить"
BTN_REFRESH = "🔄 Обновить"
BTN_INVITE = "📨 Пригласить"
BTN_START = "▶️ Запустить"
BTN_CLOSE = "🏁 Закрыть"
BTN_JOIN = "✅ Войти"
BTN_NEXT = "🔄 Следующее"
BTN_MEMBERS = "👥 Участники"
BTN_INFO = "ℹ️ Инфо"
BTN_SEARCH_AGAIN = "🔄 Искать снова"
BTN_FIND_ANOTHER = "🔎 Найти другое"
BTN_CREATE_OWN = "➕ Создать своё"
BTN_PLAY = "🎮 Играть"
BTN_SEARCH_MORE = "🔁 Искать ещё"
BTN_TRY_AGAIN = "🔁 Попробовать ещё"
BTN_RETURN_TO_LOBBY = "↩️ Вернуться в активное лобби"

CB_TOPIC_PREFIX = "lobby:topic:"
CB_CREATE_ROLE_PREFIX = "lobby:create_role:"
CB_CREATE_ROLE_PAGE_PREFIX = "lobby:create_role_page:"
CB_JOIN_ROLE_PREFIX = "lobby:join_role:"
CB_JOIN_ROLE_PAGE_PREFIX = "lobby:join_role_page:"
CB_CREATE_SEARCH_ROLE_PREFIX = "lobby:create_search_role:"
CB_JOIN_SEARCH_ROLE_PREFIX = "lobby:join_search_role:"
CB_FIND_ROLE = "lobby:find_role"
CB_RANDOM_ROLE = "lobby:random_role"
CB_RANDOM_FREE_ROLE = "lobby:random_free_role"
CB_SEARCH_MORE = "lobby:search_more"


def _reply(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
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
    rows = [[BTN_REFRESH]]
    if is_owner:
        rows.append([BTN_INVITE])
        rows.append([BTN_START])
        rows.append([BTN_CLOSE])
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
    return _reply(_with_nav(rows))


def get_lobby_info_reply_keyboard(is_owner: bool = False) -> ReplyKeyboardMarkup:
    rows = [[BTN_MEMBERS]]
    if is_owner:
        rows.append([BTN_CLOSE])
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
